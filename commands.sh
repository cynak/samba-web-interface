mkdir /opt/samba-flask
chmod 777 /opt/samba-flask
chown nobody:nogroup /opt/samba-flask
git clone https://github.com/cynak/samba-web-interface.git
chown -R samaba-flask:samba-flask /opt/samba-flask/
cd /opt/samba-flask/samba-web-interface
conda create -n samba-flask python==3.10 --file requirements.txt
conda activate samba-flask
python main.py
