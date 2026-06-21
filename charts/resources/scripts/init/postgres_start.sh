# Copyright (C) 2021 Wind River Systems, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

#!/bin/bash

# sed -i 's/huge_page=try/huge_page=off/' /usr/share/postgresql/postgresql.conf.sample
cat <<EOF >> /usr/share/postgresql/postgresql.conf.sample
huge_pages = off
max_connections = 100
shared_buffers = 24MB
EOF

PGDATA=${PGDATA:-/var/lib/postgresql/data/pgdata}
DUMP_FILE="/var/lib/postgresql/data/pg_upgrade_dump.sql"
WIPED=false

# Detect postgres major version mismatch between the binary and existing data.
# PostgreSQL internal data storage format changes between major versions, making
# PGDATA from one major version incompatible with another (e.g. 9.6->18, 18->20).
# A data migration (pg_dump/restore or pg_upgrade) is always required for major
# version upgrades — this applies to all past and future major versions.
# Ref: https://www.postgresql.org/docs/current/pgupgrade.html
# If there's a mismatch (e.g. after app upgrade/rollback changed the pg image),
# wipe PGDATA so the entrypoint reinitializes a clean data directory.
if [ -f "$PGDATA/PG_VERSION" ]; then
    EXISTING_VER=$(cat "$PGDATA/PG_VERSION")
    RUNNING_VER=$(postgres --version | awk '{split($NF,v,"."); if(v[1]>=10) print v[1]; else print v[1]"."v[2]}')
    if [ "$EXISTING_VER" != "$RUNNING_VER" ]; then
        echo "PG major version changed ($EXISTING_VER -> $RUNNING_VER). Wiping PGDATA."
        rm -rf "$PGDATA"/*
        WIPED=true
        if [ ! -f "$DUMP_FILE" ]; then
            echo "WARNING: No dump file found. Database will be reinitialized without data."
        fi
    fi
fi

# Resolve entrypoint path — differs between pg image versions.
if [ -x /usr/local/bin/docker-entrypoint.sh ]; then
    ENTRYPOINT=/usr/local/bin/docker-entrypoint.sh
else
    ENTRYPOINT=/docker-entrypoint.sh
fi

if [ -f "$DUMP_FILE" ] && [ "$WIPED" = "true" ]; then
    # Dump file exists from a prior pg_dump (lifecycle plugin runs this
    # before upgrade/downgrade). Start postgres in the background and wait
    # for it to accept TCP connections before restoring.
    # We must wait for TCP (not unix socket) because the entrypoint starts
    # a temporary socket-only postgres during initialization; TCP readiness
    # means the entrypoint has fully completed and postgres is ready for use.
    $ENTRYPOINT postgres &
    PG_PID=$!
    READY=false
    for i in $(seq 1 60); do
        if pg_isready -h 127.0.0.1 -U o2ims -q 2>/dev/null; then READY=true; break; fi
        sleep 2
    done
    if [ "$READY" != "true" ]; then
        echo "ERROR: postgres not ready after 120s, aborting restore."
        exit 1
    fi
    echo "Restoring database from upgrade dump..."
    if psql -h 127.0.0.1 -U o2ims -d o2ims -f "$DUMP_FILE" > /dev/null 2>&1; then
        rm -f "$DUMP_FILE"
        echo "Restore complete."
    else
        echo "ERROR: Restore failed, keeping dump for retry."
        exit 1
    fi
    wait $PG_PID
else
    # Normal startup — no dump to restore (or no wipe happened).
    # Clean up stale dump file if version didn't change.
    rm -f "$DUMP_FILE"
    exec $ENTRYPOINT postgres
fi

sleep infinity
