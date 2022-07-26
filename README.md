# tdt_online
opensource app to crate web inteface to working app Tovar-dengi-tovar

installing :
1.
git clone https://github.com/mrch666/tdt_online.git
2. change dir
cd tdt_online
3. crate virtual env
python3 -m venv env
activate env
. env/bin/activate
install lib
pip3 install -r requirements.txt
set env 
export FLASK_APP=run.py
export SERVER_TDT="127.0.0.1"#or yours server tdt ip_adress
flask run host=0.0.0.0
