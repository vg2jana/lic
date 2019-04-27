def_port=8000
def_ip=127.0.0.1

python3 manage.py makemigrations insurance
python3 manage.py migrate
while [[ 1 ]]
do
  printf "IP address to use [default: $def_ip][? for help]: "
  read ip
  [[ -z $ip ]] && ip=$def_ip
  if [[ $ip == '?' ]]
  then
    echo "Available IP address from this machine:"
    ifconfig|grep -w inet|awk -F'inet ' '{print $NF}'|awk '{print $1}'
    continue
  fi
  break
done
printf "Port number [default: $def_port]: "
read port
[[ -z $port ]] && port=$def_port
python3 manage.py runserver $ip:$port
