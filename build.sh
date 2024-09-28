set -o errexit

pip install -r requirements.txt

python ./point_system/manage.py collectstatic --noinput
python ./point_system/manage.py makemigrations
python ./point_system/manage.py migrate
