apt-get update && apt-get install ssh -y

if [ -z "${HELM_USER_PASSWD}" ];
then
    HELM_USER_PASSWD=St8rlingX
fi
useradd helm
passwd helm << EOF
${HELM_USER_PASSWD}
${HELM_USER_PASSWD}
EOF

service ssh restart

tail -f /dev/null