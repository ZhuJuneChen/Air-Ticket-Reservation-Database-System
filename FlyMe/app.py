import re
import secrets
import hashlib

import pymysql
from flask import Flask, redirect, request, render_template, url_for, session, jsonify

import mysql_utils

app = Flask(__name__)
conn = pymysql.connect(host='localhost', user='root', password='', database='FlyMe1.0')

cfg_filename = 'app.ini'
admin_username = ''
admin_password = ''
cnx = None


@app.route('/')
def home():
    if session.get('isLogin') and session.get('type') == 'airline_staff':
        return redirect(url_for('view_flight_airline_staff'))
    else:
        return redirect(url_for('search_flight_by_location'))


def match(form: dict, rules: dict):
    try:
        for key in form.keys():
            if key not in rules:
                return False
        for key in rules.keys():
            if key not in form:
                return False
        for name, regex in rules.items():
            if re.match(regex, form[name]) is None:
                return False
        return True
    except:
        return False


@app.route('/login/customer', methods=['GET', 'POST'])
def login_customer():
    if request.method == 'GET':
        return render_template('LoginCustomer.html')
    elif request.method == 'POST':
        rules = {'email': r'^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$',
                 'password': r'^[a-zA-Z0-9]{8}$'}
        if not match(request.form, rules):
            return render_template('LoginCustomer.html', error='Invalid form data.')
        else:
            password = hashlib.md5(request.form.get('password').encode()).hexdigest()
            result = mysql_utils.login_customer(cnx=cnx,
                                         email=request.form.get('email'),
                                         password=password)
        if result.get('login'):
            session['isLogin'] = True
            session['type'] = 'customer'
            session['email'] = result.get('email')
            session['displayName'] = result.get('name')
            session['displayType'] = 'Customer'
            return redirect(url_for('home'))
        else:
            return render_template('LoginCustomer.html',
                                   error='Either your email is not recognized or your password is incorrect.')


@app.route('/login/bookingAgent', methods=['GET', 'POST'])
def login_booking_agent():
    if request.method == 'GET':
        return render_template('LoginBookingAgent.html')
    elif request.method == 'POST':
        rules = {'email': r'^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$',
                 'password': r'^[a-zA-Z0-9]{8}$'}
        if not match(request.form, rules):
            return render_template('LoginBookingAgent.html', error='Invalid form data.')
        else:
            password = hashlib.md5(request.form.get('password').encode()).hexdigest()
            result = mysql_utils.login_booking_agent(cnx=cnx,
                                                  email=request.form.get('email'),
                                                  password=password)
            if result.get('login'):
                session['isLogin'] = True
                session['type'] = 'booking_agent'
                session['email'] = result.get('email')
                session['displayName'] = result.get('email')
                session['displayType'] = 'Booking Agent'
                return redirect(url_for('home'))
            else:
                return render_template('LoginBookingAgent.html',
                                       error='Either your email is not recognized or your password is incorrect.')


@app.route('/login/airlineStaff', methods=['GET', 'POST'])
def login_airline_staff():
    if request.method == 'GET':
        return render_template('LoginStaff.html')
    elif request.method == 'POST':
        rules = {'username': r'^.+$',
                 'password': r'^[a-zA-Z0-9]{8}$'}
        if not match(request.form, rules):
            return render_template('LoginStaff.html', error='Invalid form data.')
        else:
            password = hashlib.md5(request.form.get('password').encode()).hexdigest()
            result = mysql_utils.login_airline_staff(cnx=cnx,
                                                  username=request.form.get('username'),
                                                  password=password)
            if result.get('login'):
                session['isLogin'] = True
                session['type'] = 'airline_staff'
                session['username'] = result.get('username')
                session['displayName'] = result.get('display_name')
                session['displayType'] = 'Airline Staff'
                return redirect(url_for('home'))
            else:
                return render_template('LoginStaff.html',
                                       error='Either your username is not recognized or your password is incorrect.')


@app.route('/logout')
def logout():
    if not session.get('isLogin'):
        return redirect(url_for('home'))
    else:
        session['isLogin'] = False
        return render_template('Logout.html')


@app.route('/register/customer', methods=['GET', 'POST'])
def register_customer():
    if session.get('isLogin'):
        return redirect(url_for('home'))
    elif request.method == 'GET':
        return render_template('RegisterCustomer.html')
    elif request.method == 'POST':
        rules = {'email': r'^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$',
                 'name': r'^.+$',
                 'password': r'^[a-zA-Z0-9]{8}$',
                 'building_number': r'^.+$',
                 'street': r'^.+$',
                 'city': r'^.+$',
                 'state': r'^.+$',
                 'phone_number': r'^\d+$',
                 'date_of_birth': r'^\d{4}\/\d{2}\/\d{2}$',
                 'passport_number': r'^.+$',
                 'passport_country': r'^.+$',
                 'passport_expiration': r'^\d{4}\/\d{2}\/\d{2}$'}
        if not match(request.form, rules):
            return render_template('RegisterCustomer.html', error='Invalid form data.')
        else:
            password = hashlib.md5(request.form.get('password').encode()).hexdigest()
            result = mysql_utils.register_customer(cnx=cnx,
                                                email=request.form.get('email'),
                                                name=request.form.get('name'),
                                                password=password,
                                                building_number=request.form.get('building_number'),
                                                street=request.form.get('street'),
                                                city=request.form.get('city'),
                                                state=request.form.get('state'),
                                                phone_number=request.form.get('phone_number'),
                                                passport_number=request.form.get('passport_number'),
                                                passport_expiration=request.form.get('passport_expiration'),
                                                passport_country=request.form.get('passport_country'),
                                                date_of_birth=request.form.get('date_of_birth'))

            if result.get('good'):
                return render_template('RegisterCustomer.html', success=True)
            else:
                return render_template('RegisterCustomer.html', error=result.get('error'))


@app.route('/register/bookingAgent', methods=['GET', 'POST'])
def register_booking_agent():
    if session.get('isLogin'):
        return redirect(url_for('home'))
    elif request.method == 'GET':
        return render_template('RegisterBookingAgent.html')
    elif request.method == 'POST':
        rules = {'email': r'^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$',
                 'booking_agent_id': r'^\d+$',
                 'password': r'^[a-zA-Z0-9]{8}$'}
        if not match(request.form, rules):
            return render_template('RegisterBookingAgent.html', error='Invalid form data.')
        else:
            password = hashlib.md5(request.form.get('password').encode()).hexdigest()
            result = mysql_utils.register_booking_agent(cnx=cnx,
                                                     email=request.form.get('email'),
                                                     password=password,
                                                     booking_agent_id=request.form.get('booking_agent_id'))
            if result.get('good'):
                return render_template('RegisterBookingAgent.html', success=True)
            else:
                return render_template('RegisterBookingAgent.html', error=result.get('error'))


@app.route('/register/airlineStaff', methods=['GET', 'POST'])
def register_airline_staff():
    if session.get('isLogin'):
        return redirect(url_for('home'))
    elif request.method == 'GET':
        return render_template('RegisterStaff.html')
    elif request.method == 'POST':
        rules = {'username': r'^.+$',
                 'first_name': r'^.+$',
                 'last_name': r'^.+$',
                 'password': r'^[a-zA-Z0-9]{8}$',
                 'date_of_birth': r'^\d{4}\/\d{2}\/\d{2}$',
                 'airline_name': r'^.+$'}
        if not match(request.form, rules):
            return render_template('RegisterStaff.html', error='Invalid form data.')
        else:
            password = hashlib.md5(request.form.get('password').encode()).hexdigest()
            result = mysql_utils.register_airline_staff(cnx=cnx,
                                                     username=request.form.get('username'),
                                                     password=password,
                                                     first_name=request.form.get('first_name'),
                                                     last_name=request.form.get('last_name'),
                                                     date_of_birth=request.form.get('date_of_birth'),
                                                     airline_name=request.form.get('airline_name'))
            if result.get('good'):
                return render_template('RegisterStaff.html', success=True)
            else:
                return render_template('RegisterStaff.html', error=result.get('error'))



@app.route('/searchFlight/location', methods=['GET', 'POST'])
def search_flight_by_location():
    if request.method == 'GET':
        return render_template('SearchByLocation.html')
    elif request.method == 'POST':
        rules = {
            'source': r'^.+$',
            'destination': r'^.+$',
            'date': r'^\d{4}\/\d{2}\/\d{2}$'
        }
        if not match(request.form, rules):
            return render_template('SearchByLocation.html',
                                   error='Invalid search parameters. Please modify your search.')
        result = mysql_utils.search_flight_by_location(cnx=cnx,
                                                    source=request.form.get('source'),
                                                    destination=request.form.get('destination'),
                                                    date=request.form.get('date'))
        if result:
            head = [' '.join(w.capitalize() for w in s.split('_')) for s in result[0].keys()]
            if session.get('isLogin') and session.get('type') in ('customer', 'booking_agent'):
                data = [list(row.values()) + [
                    url_for('purchase_flight', airline_name=row.get('airline_name'), flight_num=row.get('flight_num'))]
                        for
                        row in result]
            else:
                data = [list(row.values()) + [''] for row in result]
            return render_template('SearchByLocation.html', head=head, data=data)
        else:
            return render_template('SearchByLocation.html',
                                   error="Your search found no result. Please modify your search.")


@app.route('/searchFlight/flightNum', methods=['GET', 'POST'])
def search_flight_by_flight_num():
    if request.method == 'GET':
        return render_template('SearchByFlightNum.html')
    elif request.method == 'POST':
        rules = {
            'flight_num': r'^\d+$',
            'date': r'^\d{4}\/\d{2}\/\d{2}$'
        }
        if not match(request.form, rules):
            return render_template('SearchByFlightNum.html',
                                   error='Invalid search parameters. Please modify your search.')
        result = mysql_utils.search_flight_by_flight_num(cnx=cnx,
                                                      flight_num=request.form.get('flight_num'),
                                                      date=request.form.get('date'))
        if result:
            head = [' '.join(w.capitalize() for w in s.split('_')) for s in result[0].keys()]
            if session.get('isLogin'):
                data = [list(row.values()) + [
                    url_for('purchase_flight', airline_name=row.get('airline_name'), flight_num=row.get('flight_num'))]
                        for
                        row in result]
            else:
                data = [list(row.values()) + [''] for row in result]
            return render_template('SearchByFlightNum.html', head=head, data=data)
        else:
            return render_template('SearchByFlightNum.html',
                                   error="Your search found no result. Please modify your search.")


@app.route('/purchaseFlight/<airline_name>/<flight_num>', methods=['POST'])
def purchase_flight(airline_name, flight_num):
    if session.get('isLogin') and session.get('type') in ('customer', 'booking_agent'):
        if session.get('type') == 'customer':
            result = mysql_utils.purchase_flight(cnx=cnx,
                                              customer_email=session.get('email'),
                                              airline_name=airline_name,
                                              flight_num=flight_num)
        else:
            rules = {'customer_email': r'^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$'}
            if not match(request.form, rules):
                return render_template('SearchByLocation.html', error="Customer email address is invalid.")
            result = mysql_utils.purchase_flight(cnx=cnx,
                                              customer_email=request.form.get('customer_email'),
                                              airline_name=airline_name,
                                              flight_num=flight_num,
                                              booking_agent_email=session.get('email'))
        if result.get('good'):
            return render_template('SearchByLocation.html', success=True)
        else:
            return render_template('SearchByLocation.html', error=result.get('error'))
    else:
        return redirect(url_for('home'))


@app.route('/viewMyFlight', methods=['GET', 'POST'])
def view_my_flight():
    if session.get('isLogin') and session.get('type') in ('customer', 'booking_agent'):
        if session.get('type') == 'customer':
            result = mysql_utils.view_my_flight_customer(cnx=cnx,
                                                      email=session.get('email'),
                                                      location=request.form.get('location'),
                                                      start_date=request.form.get('start_date'),
                                                      end_date=request.form.get('end_date'))
        else:
            result = mysql_utils.view_my_flight_booking_agent(
                cnx=cnx,
                email=session.get('email'),
                location=request.form.get('location'),
                start_date=request.form.get('start_date'),
                end_date=request.form.get('end_date'))
        if result:
            head = [' '.join(w.capitalize() for w in s.split('_')) for s in result[0].keys()]
            data = [list(row.values()) + [''] for row in result]
            return render_template('ViewFlight.html', head=head, data=data)
        else:
            return render_template('ViewFlight.html', error='Your search found no result. Please modify your search.')
    else:
        return redirect(url_for('home'))


@app.route('/trackMySpending', methods=['GET', 'POST'])
def track_my_spending():
    if session.get('isLogin') and session.get('type') == 'customer':
        result = mysql_utils.track_my_spending(cnx=cnx,
                                            email=session.get('email'),
                                            start_date=request.form.get('start_date'),
                                            end_date=request.form.get('end_date'))
        if result:
            return render_template('CustomerTrackSpending.html', statistic=result.get('total'),
                                   barchart_x=str(list(result.get('detail').keys())),
                                   barchart_data=str(list(result.get('detail').values())))
        else:
            return render_template('CustomerTrackSpending.html', error='Unable to display the spending statistics.')
    else:
        return redirect(url_for('home'))


@app.route('/viewMyCommission', methods=['GET', 'POST'])
def view_my_commission():
    if session.get('isLogin') and session.get('type') == 'booking_agent':
        result = mysql_utils.view_my_commission(cnx=cnx,
                                             email=session.get('email'),
                                             start_date=request.form.get('start_date'),
                                             end_date=request.form.get('end_date'))
        if result:
            return render_template('ViewCommision.html',
                                   commission=result.get('commission'),
                                   flight=result.get('flight'),
                                   average=result.get('average'))
        else:
            return render_template('ViewCommision.html', error='Unable to display the commission statistics.')
    else:
        return redirect(url_for('home'))


@app.route('/viewTopCustomers')
def view_top_customers():
    if session.get('isLogin') and session.get('type') == 'booking_agent':
        result = mysql_utils.view_top_customers(cnx=cnx,
                                             email=session.get('email'))
        if result:
            return render_template('ViewTopCustomer.html',
                                   commission_x=list(result.get('commission').keys()),
                                   commission_data=list(result.get('commission').values()),
                                   ticket_x=list(result.get('ticket').keys()),
                                   ticket_data=list(result.get('ticket').values()))
        else:
            return render_template('ViewTopCustomer.html', error='Unable to display the top customer statistics.')
    else:
        return redirect(url_for('home'))


@app.route('/airlineStaff/manageFlight', methods=['GET', 'POST'])
def view_flight_airline_staff():
    if session.get('isLogin') and session.get('type') == 'airline_staff':
        result = mysql_utils.view_my_flight_airline_staff(cnx=cnx,
                                                       username=session.get('username'),
                                                       location=request.form.get('location'),
                                                       start_date=request.form.get('start_date'),
                                                       end_date=request.form.get('end_date'))
        if result:
            head = [' '.join(w.capitalize() for w in s.split('_')) for s in result[0].keys()]
            data = [list(row.values())
                #     + [
                # url_for('view_passengers', airline_name=row.get('airline_name'), flight_num=row.get('flight_num')),
                # url_for('update_status', airline_name=row.get('airline_name'), flight_num=row.get('flight_num'))]
                    for
                    row in result]
            return render_template('ManageFlight.html', head=head, data=data)
        else:
            return render_template('ManageFlight.html', error='Sorry, no flight.')
    else:
        return redirect(url_for('home'))


@app.route('/airlineStaff/ViewCustomersOnBoard/<airline_name>/<flight_num>')
def view_passengers(airline_name, flight_num):
    if session.get('isLogin') and session.get('type') == 'airline_staff':
        result = mysql_utils.view_passengers(cnx=cnx,
                                          airline_staff_username=session.get('username'),
                                          airline_name=airline_name,
                                          flight_num=flight_num)
        if result:
            return render_template('ViewCustomersOnBoard.html', airline_name=airline_name, flight_num=flight_num, data=result)
        else:
            return render_template('ViewCustomersOnBoard.html', airline_name=airline_name, flight_num=flight_num,
                                   error='No data.')
    else:
        return redirect(url_for('home'))

@app.route('/airlineStaff/UpdateStatus/<airline_name>/<flight_num>', methods=['POST'])
def update_status(airline_name, flight_num):
    if session.get('isLogin') and session.get('type') == 'airline_staff':
        if not request.form.get('new_status'):
            return render_template('UpdateStatus.html', error='New status cannot be empty.')
        result = mysql_utils.update_status(cnx=cnx,
                                        airline_staff_username=session.get('username'),
                                        airline_name=airline_name,
                                        flight_num=flight_num,
                                        new_status=request.form.get('new_status'))
        if result.get('good'):
            return render_template('UpdateStatus.html', success='You have updated the flight status.')
        else:
            return render_template('UpdateStatus.html',
                                   error='Unable to update the flight status: %s' % result.get('error'))
    else:
        return redirect(url_for('home'))


@app.route('/airlineStaff/addFlight', methods=['POST'])
def add_flight():
    if session.get('isLogin') and session.get('type') == 'airline_staff':
        rules = {'departure_airport': r'^.+$',
                 'departure_time': r'^\d{3,4}\/\d{2}\/\d{2} \d{1,2}\:\d{2}$',
                 'arrival_airport': r'^.+$',
                 'arrival_time': r'^\d{3,4}\/\d{2}\/\d{2} \d{1,2}\:\d{2}$',
                 'flight_num': r'^\d+$',
                 'price': r'^[0-9|.]+$',
                 'status': r'^.+$',
                 'airplane_id': r'^\d+$'}
        if not match(request.form, rules):
            return render_template('AddFlight.html',
                                   error='Unable to add flight due to invalid form data.')
        else:
            result = mysql_utils.add_flight(cnx=cnx,
                                         airline_staff_username=session.get('username'),
                                         flight_num=request.form.get('flight_num'),
                                         departure_airport=request.form.get('departure_airport'),
                                         departure_time=request.form.get('departure_time'),
                                         arrival_airport=request.form.get('arrival_airport'),
                                         arrival_time=request.form.get('arrival_time'),
                                         price=request.form.get('price'),
                                         status=request.form.get('status'),
                                         airplane_id=request.form.get('airplane_id'))
            if result.get('good'):
                return render_template('AddFlight.html', success='You have added the flight.')
            else:
                return render_template('AddFlight.html',
                                       error='Unable to add flight: %s' % result.get('error'))
    else:
        return redirect(url_for('home'))


@app.route('/airlineStaff/addAirplane', methods=['GET', 'POST'])
def add_airplane():
    if session.get('isLogin') and session.get('type') == 'airline_staff':
        if request.method == 'GET':
            result_query = mysql_utils.get_airplane(cnx=cnx,
                                                 airline_staff_username=session.get('username'))
            if result_query:
                head = [' '.join(w.capitalize() for w in s.split('_')) for s in result_query[0].keys()]
                data = [list(row.values()) for row in result_query]
                return render_template('AddAirplane.html', head=head, data=data)
            else:  # nothing returned
                return render_template('AddAirplane.html', error='Airplane not found.')
        elif request.method == 'POST':
            rules = {'airplane_id': r'^\d+$',
                     'seats': r'^\d+$'}
            if not match(request.form, rules):
                return render_template('AddAirplane.html', error='Invalid form data.')
            result_exec = mysql_utils.add_airplane(cnx=cnx,
                                                airline_staff_username=session.get('username'),
                                                airplane_id=request.form.get('airplane_id'),
                                                seats=request.form.get('seats'))
            if result_exec.get('good'):
                return render_template('AddAirplane.html', success=True)
            else:
                return render_template('AddAirplane.html', error='Failed to add airplane: %s' % result_exec.get('error'))
    else:
        return redirect(url_for('home'))


@app.route('/airlineStaff/addAirport', methods=['GET', 'POST'])
def add_airport():
    if session.get('isLogin') and session.get('type') == 'airline_staff':
        if request.method == 'GET':
            result_query = mysql_utils.get_airport(cnx=cnx)
            if result_query:
                head = [' '.join(w.capitalize() for w in s.split('_')) for s in result_query[0].keys()]
                data = [list(row.values()) for row in result_query]
                return render_template('AddAirport.html', head=head, data=data)
            else:  # nothing returned
                return render_template('AddAirport.html', error='Airport not found.')
        elif request.method == 'POST':
            rules = {'airport_name': r'^.+$',
                     'airport_city': r'^.+$'}
            if not match(request.form, rules):
                return render_template('AddAirport.html', error='Invalid form data.')
            result_exec = mysql_utils.add_airport(cnx=cnx,
                                               airport_name=request.form.get('airport_name'),
                                               airport_city=request.form.get('airport_city'))
            if result_exec.get('good'):
                return render_template('AddAirport.html', success=True)
            else:
                return render_template('AddAirport.html', error='Failed to add airport: %s' % result_exec.get('error'))
    else:
        return redirect(url_for('home'))


@app.route('/airlineStaff/viewTopBookingAgents')
def view_top_booking_agents():
    if session.get('isLogin') and session.get('type') == 'airline_staff':
        result = mysql_utils.view_top_booking_agents(cnx=cnx,
                                                  airline_staff_username=session.get('username'))
        if result.get('ticket_month'):
            xtm = [' '.join(w.capitalize() for w in s.split('_')) for s in result.get('ticket_month')[0].keys()]
            ytm = [list(row.values()) for row in result.get('ticket_month')]
            xty = [' '.join(w.capitalize() for w in s.split('_')) for s in result.get('ticket_year')[0].keys()]
            yty = [list(row.values()) for row in result.get('ticket_year')]
            xc = [' '.join(w.capitalize() for w in s.split('_')) for s in result.get('commission')[0].keys()]
            yc = [list(row.values()) for row in result.get('commission')]
            return render_template('ViewTopBookingAgent.html',
                                   xtm=xtm, ytm=ytm,
                                   xty=xty, yty=yty,
                                   xc=xc, yc=yc)
        else:
            return render_template('ViewTopBookingAgent.html', error='Unable to display top booking agents data.')
    else:
        return redirect(url_for('home'))


@app.route('/airlineStaff/viewFrequentCustomer')
def view_frequent_customer():
    if session.get('isLogin') and session.get('type') == 'airline_staff':
        result = mysql_utils.view_frequent_customer(cnx=cnx,
                                                 airline_staff_username=session.get('username'))
        if result:
            return render_template('ViewFrequentCustomer.html', email=result)
        else:
            return render_template('ViewFrequentCustomer.html',
                                   error='Unable to display the most frequent customer data.')
    else:
        return redirect(url_for('home'))


@app.route('/airlineStaff/viewCustomerFlightHistory', methods=['GET', 'POST'])
def view_customer_flight_history():
    if session.get('isLogin') and session.get('type') == 'airline_staff':
        if request.method == 'GET':
            return render_template('ViewCustomerFlight.html')
        elif request.method == 'POST':
            rules = {'customer_email': r'^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$'}
            if not match(request.form, rules):
                return render_template('ViewCustomerFlight.html',
                                       error='Unable to display history due to invalid email address.')
            result = mysql_utils.view_customer_flight_history(cnx=cnx,
                                                           airline_staff_username=session.get('username'),
                                                           customer_email=request.form.get('customer_email'))
            if result:
                head = [' '.join(w.capitalize() for w in s.split('_')) for s in result[0].keys()]
                data = [list(row.values()) for row in result]
                return render_template('ViewCustomerFlight.html', head=head, data=data)
            else:
                return render_template('ViewCustomerFlight.html',
                                       error='Unable to display customer flight history.')
    else:
        return redirect(url_for('home'))


@app.route('/airlineStaff/totalTicketSold', methods=['GET', 'POST'])
def view_report():
    if session.get('isLogin') and session.get('type') == 'airline_staff':
        result_my = mysql_utils.total_ticket(cnx=cnx,
                                             airline_staff_username=session.get('username'))
        result_g = mysql_utils.view_report(cnx=cnx,
                                           airline_staff_username=session.get('username'),
                                           start_date=request.form.get('start_date'),
                                           end_date=request.form.get('end_date'))
        if result_my or result_g:
            return render_template('TicketSales.html', barchart_x=str(list(result_g.keys())),
                                   barchart_data=str(list(result_g.values())), month=result_my.get('last_month'),
                                   year=result_my.get('last_year'))
        else:
            return render_template('TicketSales.html', error='Unable to display total ticket sold data.')
    else:
        return redirect(url_for('home'))


@app.route('/airlineStaff/compareRevenue')
def compare_revenue():
    if session.get('isLogin') and session.get('type') == 'airline_staff':
        result = mysql_utils.compare_revenue(cnx=cnx,
                                          airline_staff_username=session.get('username'))
        if result:
            return render_template('CompareRevenue.html',
                                   md=result.get('md'),
                                   mi=result.get('mi'),
                                   yd=result.get('yd'),
                                   yi=result.get('yi'))
        else:
            return render_template('CompareRevenue.html', error='Unable to display revenue data.')
    else:
        return redirect(url_for('home'))


@app.route('/airlineStaff/viewTopDestinations')
def view_top_destinations():
    if session.get('isLogin') and session.get('type') == 'airline_staff':
        result = mysql_utils.view_top_destinations(cnx=cnx,
                                                airline_staff_username=session.get('username'))
        if result.get('month'):
            return render_template('ViewTopDestination.html', month=result.get('month'), year=result.get('year'))
        else:
            return render_template('ViewTopDestination.html', error='Unable to display top destinations data.')
    else:
        return redirect(url_for('home'))



@app.route('/getAllAirlines', methods=['POST'])
def get_all_airlines():
        return jsonify(mysql_utils.get_all_airlines(cnx=cnx))



@app.route('/getAllCitiesAndAirports', methods=['POST'])
def get_all_cities_and_airports():
    return jsonify(mysql_utils.get_all_cities_and_airports(cnx=cnx))


@app.route('/getAllCustomerEmails', methods=['POST'])
def get_all_customer_emails():
    if session.get('isLogin') and session.get('type') in ('booking_agent', 'airline_staff'):
        return jsonify(mysql_utils.get_all_customer_emails(cnx=cnx))
    else:
        return jsonify([])


@app.route('/getAllAirports', methods=['POST'])
def get_all_airports():
    if session.get('isLogin') and session.get('type') == 'airline_staff':
        return jsonify(mysql_utils.get_all_airports(cnx=cnx))
    else:
        return jsonify([])


@app.route('/getAllAirplaneId', methods=['POST'])
def get_all_airplane_id():
    if session.get('isLogin') and session.get('type') == 'airline_staff':
        return jsonify(mysql_utils.get_all_airplane_id(cnx=cnx))
    else:
        return jsonify([])


if __name__ == '__main__':
    app_setup = True
    cnx = {'host': 'localhost',
                   'user': 'root',
                   'password': '',
                   'database': 'FlyMe1.0',
                   'autocommit': False,
                   'cursorclass': pymysql.cursors.DictCursor}
    app.secret_key = secrets.token_urlsafe(16)
    app.run(host="127.0.0.1",
            port=5000,
            debug=False)
