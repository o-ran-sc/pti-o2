apk add --no-cache openssh

if [ -z "${HELM_USER_PASSWD}" ];
then
    HELM_USER_PASSWD=St8rlingX*
fi

adduser helm << EOF
${HELM_USER_PASSWD}
${HELM_USER_PASSWD}
EOF

ssh-keygen -A
exec /usr/sbin/sshd -D -e "$@"