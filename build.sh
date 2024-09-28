set -o errexit

source /opt/render/project/src/.venv/bin/activate

pip install -r requirements.txt

python ./point_system/manage.py collectstatic --noinput
python ./point_system/manage.py makemigrations
python ./point_system/manage.py migrate
