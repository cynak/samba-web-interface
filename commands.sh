mkdir /opt/samba-flask
#create samba-flask group
groupadd samba-flask
./add_samba_to_sudo.sh
chmod 777 /opt/samba-flask
chown nobody:nogroup /opt/samba-flask
git clone https://github.com/cynak/samba-web-interface.git
chown -R samba-flask:samba-flask /opt/samba-flask/
cd /opt/samba-flask/samba-web-interface
conda create -n samba-flask python==3.10 --file requirements.txt
conda activate samba-flask
python main.py
