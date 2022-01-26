#!/usr/bin/env bash

mongosh "mongodb+srv://cluster0.s2exf.mongodb.net/myFirstDatabase?authSource=%24external&authMechanism=MONGODB-X509" --tls --tlsCertificateKeyFile $HOME/.ssh/X509-cert-4088494199104477002.pem
