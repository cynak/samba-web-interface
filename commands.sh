mkdir /opt/samba-flask
chmod +x ./add_samba_to_sudo.sh
chmod +x ./add_user_to_group.sh
#create samba-flask group
./add_samba_to_sudo.sh
./add_user_to_group.sh
chmod 777 /opt/samba-flask
chown nobody:nogroup /opt/samba-flask
git clone https://github.com/cynak/samba-web-interface.git
chown -R samba-flask:samba-flask /opt/samba-flask/
cd /opt/samba-flask/samba-web-interface
#copy the samba-flask.service file to /etc/systemd/system
sudo cp samba-flask.service /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl enable samba-flask
sudo systemctl start samba-flask
