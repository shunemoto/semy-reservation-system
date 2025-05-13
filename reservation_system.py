from flask import Flask, render_template, request, redirect
import csv

app = Flask(__name__)

def get_waiting_list():
    with open('reservations.csv', mode='r', newline='') as file:
        reader = csv.reader(file)
        waiting_list = []
        for row in reader:
            if row:
                waiting_list.append({'reservation_order': int(row[0]), 'user_name': row[1]})
        return waiting_list

def process_reservation(user_name, reservation_order=None):
    waiting_list = get_waiting_list()

    if reservation_order is None:
        reservation_order = len(waiting_list) + 1
    else:
        for i in range(len(waiting_list)):
            if waiting_list[i]['reservation_order'] >= reservation_order:
                waiting_list[i]['reservation_order'] += 1

    waiting_list.append({'reservation_order': reservation_order, 'user_name': user_name})

    waiting_list.sort(key=lambda x: x['reservation_order'])
    with open('reservations.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        for entry in waiting_list:
            writer.writerow([entry['reservation_order'], entry['user_name']])

@app.route('/')
def index():
    waiting_list = get_waiting_list()
    return render_template('index.html', waiting_list=waiting_list)

@app.route("/reserve", methods=['GET', 'POST'])
def reserve():
    if request.method == 'GET':
        user_name = request.args.get('user_name')
        return render_template('reserve.html', user_name=user_name)

    elif request.method == 'POST':
        user_name = request.form['user_name']
        reservation_order = request.form.get('reservation_order')
        reservation_order = int(reservation_order) if reservation_order else None

        process_reservation(user_name, reservation_order)

        return redirect('/')