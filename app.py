from flask import Flask, render_template, flash, request, url_for, redirect, session, g
from util import query_fetch, query_mod, fetch_all, replace
from config import DB, secret_key
from hashlib import md5
from random import *
import time
import datetime
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key


@app.route('/', methods=['GET'])
def home_page_get():
    return render_template("index.html")

@app.route('/', methods=['POST'])
def home_page_post():
    source_airport = replace(request.form.get('source_airport'))
    source_city = replace(request.form.get('source_city'))
    destination_airport = replace(request.form.get('destination_airport'))
    destination_city = replace(request.form.get('destination_city'))
    arrival_date = replace(request.form.get('arrival_date'))
    city_departure_date = replace(request.form.get('city_date'))
    airport_departure_date = replace(request.form.get('airport_date'))
    departure_date = replace(request.form.get('departure_date'))
    flight_number = replace(request.form.get('flight_number'))

    # Query flight based on airport
    if source_airport:
        sql = "SELECT * FROM flight WHERE departure_airport = '{}' AND arrival_airport = '{}'" \
          " AND DATE(departure_time) = '{}'".format(source_airport, destination_airport, airport_departure_date)
        print(sql)
        response = fetch_all(sql, DB)
        print(response)
        return render_template('index.html', flights1=response)
    # Query flight based on city
    elif source_city:
        sql = "SELECT * FROM flight WHERE departure_city = '{}' AND arrival_city = '{}'" \
          " AND DATE(departure_time) = '{}'".format(source_city, destination_city, city_departure_date)
        print(sql)
        response = fetch_all(sql, DB)
        print(response)
        return render_template('index.html', flights1=response)
    # Query flight status
    elif flight_number:
        sql = "SELECT * FROM flight WHERE flight_num = '{}' AND DATE(arrival_time) = '{}'" \
          " AND DATE(departure_time) = '{}'".format(flight_number, arrival_date, departure_date)
        print(sql)
        response = fetch_all(sql, DB)
        print(response)
        return render_template('index.html', flights2=response)
    return render_template('index.html')


@app.route('/home/customer/', methods=['GET', 'POST'])
def customer_page():
    print(session['user'])
    print(session['type'])
    source_airport = replace(request.form.get('source_airport'))
    source_city = replace(request.form.get('source_city'))
    destination_airport = replace(request.form.get('destination_airport'))
    destination_city = replace(request.form.get('destination_city'))
    city_departure_date = replace(request.form.get('city_date'))
    airport_departure_date = replace(request.form.get('airport_date'))
    purchase_airline = replace(request.form.get('purchase_airline'))
    purchase_flight = replace(request.form.get('purchase_flight'))
    from_date = replace(request.form.get('from_date'))
    to_date = replace(request.form.get('to_date'))

    # if user session is customer
    if g.type == 'customer':
        one_year_ago = date.today() + relativedelta(months=-12)
        six_months_ago = date.today() + relativedelta(months=-6)
        # six months spending graph
        sql = "SELECT SUM(price) AS total, YEAR(purchase_date) AS y, MONTH(purchase_date) AS m FROM purchases NATURAL JOIN ticket " \
              "NATURAL JOIN flight WHERE customer_email = '{}' AND purchase_date >= '{}' GROUP BY YEAR(purchase_date), MONTH" \
              "(purchase_date)".format(g.user, six_months_ago)
        print('six month spending SQL: ', sql)
        six_months = fetch_all(sql, DB)
        print('six_months', six_months)

        # one year spending
        sql = "SELECT SUM(price) AS dey FROM purchases NATURAL JOIN ticket NATURAL JOIN flight WHERE customer_email = '{}' AND " \
              "purchase_date >= '{}'".format(g.user, one_year_ago)
        print('one year spending SQL: ', sql)
        one_year = fetch_all(sql, DB)
        print('one year', one_year)

        # Show my flights
        sql = "SELECT * FROM flight, purchases, ticket WHERE purchases.ticket_id = ticket.ticket_id AND ticket.flight_num = " \
              "flight.flight_num AND purchases.customer_email = '{}'".format(g.user)
        print('my_flights SQL: ', sql)
        my_flights = fetch_all(sql, DB)
        print('my_flights response: ', my_flights)

        if from_date:
            # custom range spending: total
            sql = "SELECT SUM(price) AS dey FROM purchases NATURAL JOIN ticket NATURAL JOIN flight WHERE customer_email = '{}' AND " \
                  "purchase_date <= '{}' AND purchase_date >= '{}'".format(g.user, to_date, from_date)
            print('spend_range1 SQL: ', sql)
            spend_range1 = fetch_all(sql, DB)
            print('spend_range1', spend_range1)

            # custom range spending: monthly
            sql = "SELECT SUM(price) AS total, YEAR(purchase_date) AS y, MONTH(purchase_date) AS m FROM purchases NATURAL JOIN ticket " \
                  "NATURAL JOIN flight WHERE customer_email = '{}' AND purchase_date >= '{}' AND purchase_date <= '{}' GROUP BY YEAR(purchase_date), MONTH" \
                  "(purchase_date)".format(g.user, from_date, to_date)
            print('spend_range2 SQL: ', sql)
            spend_range2 = fetch_all(sql, DB)
            print('spend_range2', spend_range2)

            return render_template("customer_home.html", username=session['user'],six_months=six_months, Data=my_flights,
                                   one_year=one_year, spend_range1=spend_range1, spend_range2=spend_range2)

        # Buy Ticket
        if purchase_airline:
            ticket_ID = randint(1, 99999999)
            sql = "INSERT INTO ticket VALUES ('{}', '{}', '{}')".format(ticket_ID, purchase_airline, purchase_flight)
            print("book ticket(ticket table) SQL: ", sql)
            result = query_mod(sql, DB)
            if result == 1:
                flash('Request denied, please try again!')
            sql = "INSERT INTO purchases(ticket_id, customer_email, purchase_date) VALUES ('{}', '{}', '{}')".format(ticket_ID, g.user, time.strftime("%Y-%m-%d"))
            print("book ticket(ticket table) SQL: ", sql)
            result = query_mod(sql, DB)
            if result == 1:
                flash('Request denied, please try again!')


        # Query flight based on airport
        if source_airport:
            sql = "SELECT * FROM flight WHERE departure_airport = '{}' AND arrival_airport = '{}'" \
              " AND DATE(departure_time) = '{}'".format(source_airport, destination_airport, airport_departure_date)
            print(sql)
            response = fetch_all(sql, DB)
            print(response)
            return render_template('customer_home.html', username=session['user'], flights=response, Data=my_flights,
                                   six_months=six_months, one_year=one_year)
        # Query flight based on city
        elif source_city:
            sql = "SELECT * FROM flight WHERE departure_city = '{}' AND arrival_city = '{}'" \
              " AND DATE(departure_time) = '{}'".format(source_city, destination_city, city_departure_date)
            print(sql)
            response = fetch_all(sql, DB)
            print(response)
            return render_template('customer_home.html', username=session['user'], flights=response, Data=my_flights,
                                   six_months=six_months, one_year=one_year)
        # If the user logged in a session with customer account
        return render_template("customer_home.html", username=session['user'], Data=my_flights, six_months=six_months,
                               one_year=one_year)
    print('invalid session type')
    return redirect(url_for('home_page_get'))


@app.route('/home/agent/', methods=['GET', 'POST'])
def agent_page():
    print(session['user'])
    print(session['type'])
    source_airport = replace(request.form.get('source_airport'))
    source_city = replace(request.form.get('source_city'))
    destination_airport = replace(request.form.get('destination_airport'))
    destination_city = replace(request.form.get('destination_city'))
    city_departure_date = replace(request.form.get('city_date'))
    airport_departure_date = replace(request.form.get('airport_date'))
    customer_ID = replace(request.form.get('purchase_customer'))
    purchase_airline = replace(request.form.get('purchase_airline'))
    purchase_flight = replace(request.form.get('purchase_flight'))
    from_date = replace(request.form.get('from_date'))
    to_date = replace(request.form.get('to_date'))

    if g.type == 'agent':
        sql = "SELECT booking_agent_id FROM booking_agent WHERE email = '{}'".format(g.user)
        booking_agent_ID = fetch_all(sql, DB)
        #view top 5 customers tickects
        end_date = datetime.date.today()
        start_date = end_date - timedelta(days=183)
        sql = "SELECT customer.email as customer_email, COUNT(distinct ticket_id) AS tickets FROM purchases NATURAL JOIN ticket NATURAL JOIN flight, customer WHERE booking_agent_id = '{}' AND purchases.customer_email = customer.email AND " \
                  "purchase_date <= '{}' AND purchase_date >= '{}' GROUP BY customer_email ORDER BY tickets DESC LIMIT 5".format(booking_agent_ID[0]['booking_agent_id'], end_date, start_date)
        top_cus1 = fetch_all(sql, DB)
        print(top_cus1)

        #view top 5 customers commission
        end_date = datetime.date.today()
        start_date = end_date - timedelta(days=365)
        sql = "SELECT customer.email as customer_email, SUM(price)*0.1 AS commission FROM purchases NATURAL JOIN ticket NATURAL JOIN flight, customer WHERE booking_agent_id = '{}' AND purchases.customer_email = customer.email AND " \
                  "purchase_date <= '{}' AND purchase_date >= '{}' GROUP BY customer_email ORDER BY commission DESC LIMIT 5".format(booking_agent_ID[0]['booking_agent_id'], end_date, start_date)
        top_cus2 = fetch_all(sql, DB)
        for i in top_cus2:
            print(i)

        #commission
        end_date = datetime.date.today()
        start_date = end_date - timedelta(days=30)
        sql = "SELECT SUM(price)*0.1 AS commission, COUNT(distinct ticket_id) AS ticket, (SUM(price)*0.1/COUNT(distinct ticket_id)) AS average FROM purchases NATURAL JOIN ticket NATURAL JOIN flight WHERE booking_agent_id = '{}' AND " \
                  "purchase_date <= '{}' AND purchase_date >= '{}'".format(booking_agent_ID[0]['booking_agent_id'], end_date, start_date)
        commission = fetch_all(sql, DB)
        print(commission)
        if not commission:
            commission = {['commission']:'0', ['ticket']:'0', ['average']:'0'}

        # Show my flights
        sql = "SELECT distinct * FROM flight, purchases, ticket WHERE purchases.ticket_id = ticket.ticket_id AND ticket.flight_num = " \
              "flight.flight_num AND purchases.booking_agent_id = '{}'".format(booking_agent_ID[0]['booking_agent_id'])
        print('my_flights SQL: ', sql)
        my_flights = fetch_all(sql, DB)
        print('my_flights response: ', my_flights)

        #specify date
        if from_date:
            sql = "SELECT booking_agent_id FROM booking_agent WHERE email = '{}'".format(g.user)
            booking_agent_ID = fetch_all(sql, DB)
            sql = "SELECT SUM(price)*0.1 AS commission, COUNT(distinct ticket_id) AS ticket, (SUM(price)*0.1/COUNT(distinct ticket_id)) AS average FROM purchases NATURAL JOIN ticket NATURAL JOIN flight WHERE booking_agent_id = '{}' AND " \
                  "purchase_date <= '{}' AND purchase_date >= '{}'".format(booking_agent_ID[0]['booking_agent_id'], to_date, from_date)
            print('Commission1 SQL: ', sql)
            commission1 = fetch_all(sql, DB)
            print('Commission1', commission1)

            return render_template("agent_home.html", username=session['user'], Data=my_flights, commission1=commission1, commission=commission, top_cus1=top_cus1,top_cus2 = top_cus2)

        
        # Query flight based on airport
        if source_airport:
            sql = "SELECT * FROM flight WHERE departure_airport = '{}' AND arrival_airport = '{}'" \
              " AND DATE(departure_time) = '{}'".format(source_airport, destination_airport, airport_departure_date)
            print(sql)
            response = fetch_all(sql, DB)
            print(response)
            return render_template('agent_home.html', username=session['user'], Data=my_flights, flights=response, commission=commission, top_cus1=top_cus1, top_cus2 = top_cus2)
        # Query flight based on city
        elif source_city:
            sql = "SELECT * FROM flight WHERE departure_city = '{}' AND arrival_city = '{}'" \
              " AND DATE(departure_time) = '{}'".format(source_city, destination_city, city_departure_date)
            print(sql)
            response = fetch_all(sql, DB)
            print(response)
            return render_template('agent_home.html', username=session['user'], Data=my_flights, flights=response, commission=commission, top_cus1=top_cus1, top_cus2 = top_cus2)

        # Buy Ticket
        if purchase_airline:
            ticket_ID = randint(1, 99999999)
            sql = "INSERT INTO ticket VALUES ('{}', '{}', '{}')".format(ticket_ID, purchase_airline, purchase_flight)
            print("book ticket(ticket table) SQL: ", sql)
            result= query_mod(sql, DB)
            if result == 1:
                flash('Request denied, please try again!')
            sql = "SELECT booking_agent_id FROM booking_agent WHERE email = '{}'".format(g.user)
            booking_agent_ID = fetch_all(sql, DB)
            sql = "INSERT INTO purchases(ticket_id, customer_email, purchase_date, booking_agent_id) VALUES ('{}', '{}', '{}', '{}')".format(ticket_ID, customer_ID, time.strftime("%Y-%m-%d"), booking_agent_ID[0]['booking_agent_id'])
            print("book ticket(ticket table) SQL: ", sql)
            result = query_mod(sql, DB)
            if result == 1:
                flash('Request denied, please try again!')


        return render_template("agent_home.html", username=session['user'], Data=my_flights, commission=commission, top_cus1=top_cus1, top_cus2 = top_cus2)
    return redirect(url_for('home_page_get'))


@app.route('/home/staff/', methods=['GET', 'POST'])
def staff_page():
    print(session['user'])
    print(session['type'])

    sql = "SELECT airline_name FROM airline_staff WHERE username = '{}'".format(g.user)
    staff_airline = query_fetch(sql, DB)
    print(staff_airline)
    # view my flights
    source_city = replace(request.form.get('source_city'))
    destination_city = replace(request.form.get('destination_city'))
    city_date = replace(request.form.get('city_date'))
    source_airport = replace(request.form.get('source_airport'))
    destination_airport = replace(request.form.get('destination_airport'))
    airport_date = replace(request.form.get('airport_date'))
    flight_number1 = replace(request.form.get('flight_number1'))
    flight_from_date = replace(request.form.get('flight_from_date'))
    flight_to_date = replace(request.form.get('flight_to_date'))

    # create new flights
    airline_name = replace(request.form.get('airline_name'))
    flight_number = replace(request.form.get('flight_number'))
    departure_airport = replace(request.form.get('departure_airport'))
    arrival_airport = replace(request.form.get('arrival_airport'))
    departure_time = replace(request.form.get('departure_time'))
    airplane_id = replace(request.form.get('airplane_id'))
    arrival_time = replace(request.form.get('arrival_time'))
    status = replace(request.form.get('status'))
    price = replace(request.form.get('price'))
    departure_city = replace(request.form.get('departure_city'))
    arrival_city = replace(request.form.get('arrival_city'))

    # change status of flights
    status_source_city = replace(request.form.get('status_source_city'))
    status_source_airport = replace(request.form.get('status_source_airport'))
    change_status = replace(request.form.get('change_status'))

    # add airplane in the system
    airline_name_plane = replace(request.form.get('airline_name_plane'))
    airplane_id_plane = replace(request.form.get('airplane_id_plane'))
    seat = replace(request.form.get('seat'))

    # add new airport in the system
    airport_name = replace(request.form.get('airport_name'))
    airport_city = replace(request.form.get('airport_city'))

    # search particular customer and airline
    freq_customer_email = replace(request.form.get('freq_customer_email'))

    # view reports
    report_from_date = replace(request.form.get('report_from_date'))
    report_to_date = replace(request.form.get('report_to_date'))

    if g.type == 'staff':
        # view all the booking agents
        # top 5 agent based on sales past year
        end_date = datetime.date.today()
        start_date = end_date - timedelta(days=365)
        sql = "SELECT booking_agent.email AS email, COUNT(distinct ticket_id) AS tickets FROM purchases NATURAL JOIN ticket " \
              "NATURAL JOIN flight NATURAL JOIN booking_agent WHERE purchase_date >= '{}' AND purchase_date <= '{}' GROUP BY booking_agent.email ORDER BY tickets DESC LIMIT 5".format(start_date, end_date)
        agent_ticket = fetch_all(sql, DB)
        print(agent_ticket)

        # top 5 agent based on sales past month
        end_date = datetime.date.today()
        start_date = end_date - timedelta(days=30)
        sql = "SELECT booking_agent.email AS email, COUNT(distinct ticket_id) AS tickets FROM purchases NATURAL JOIN ticket " \
              "NATURAL JOIN flight NATURAL JOIN booking_agent WHERE purchase_date >= '{}' AND purchase_date <= '{}' GROUP BY booking_agent.email ORDER BY tickets DESC LIMIT 5".format(start_date, end_date)
        agent_ticket_month = fetch_all(sql, DB)
        print(agent_ticket)

        # top 5 agent based on comission past year
        end_date = datetime.date.today()
        start_date = end_date - timedelta(days=365)
        sql = "SELECT booking_agent.email AS email, SUM(price)*0.1 AS commission FROM purchases NATURAL JOIN ticket NATURAL " \
              "JOIN flight NATURAL JOIN booking_agent WHERE purchase_date >= '{}' AND purchase_date <= '{}' GROUP BY booking_agent.email ORDER BY commission DESC LIMIT 5".format(start_date, end_date)
        agent_commission = fetch_all(sql, DB)
        print(agent_commission)

        # most frequent customer
        end_date = datetime.date.today()
        start_date = end_date - timedelta(days=365)
        sql = "SELECT customer_email AS email FROM purchases WHERE purchase_date >= '{}' AND purchase_date <= '{}' GROUP BY customer_email ORDER BY COUNT(customer_email) DESC LIMIT 1".format(start_date, end_date)
        print(sql)
        frequent_customer = fetch_all(sql, DB)
        print(frequent_customer)

        # view top destinations
        end_date = datetime.date.today()
        start_date = end_date - timedelta(days=90)
        sql = "SELECT arrival_city FROM flight NATURAL JOIN purchases WHERE purchase_date >= '{}' AND purchase_date <= '{}' GROUP BY arrival_city ORDER BY COUNT(arrival_city) DESC LIMIT 3".format(start_date, end_date)
        print(sql)
        top_destinations1 = fetch_all(sql, DB)
        print(top_destinations1)

        end_date = datetime.date.today()
        start_date = end_date - timedelta(days=365)
        sql = "SELECT arrival_city FROM flight NATURAL JOIN purchases WHERE purchase_date >= '{}' AND purchase_date <= '{}' GROUP BY arrival_city ORDER BY COUNT(arrival_city) DESC LIMIT 3".format(start_date, end_date)
        print(sql)
        top_destinations2 = fetch_all(sql, DB)
        print(top_destinations2)

        # comparison of revenue earned
        labels2 = []
        end_date = datetime.date.today()
        start_date = end_date - timedelta(days=30)
        sql = "SELECT SUM(price) AS v FROM flight NATURAL JOIN purchases WHERE booking_agent_id IS NOT NULL AND purchase_date >= '{}' AND purchase_date <= '{}'".format(start_date, end_date)
        labels2.extend(fetch_all(sql, DB))

        sql = "SELECT SUM(price) AS v FROM flight NATURAL JOIN purchases WHERE booking_agent_id IS NULL AND purchase_date >= '{}' AND purchase_date <= '{}'".format(start_date, end_date)
        labels2.extend(fetch_all(sql, DB))

        end_date = datetime.date.today()
        start_date = end_date - timedelta(days=365)
        sql = "SELECT SUM(price) AS v FROM flight NATURAL JOIN purchases WHERE booking_agent_id IS NOT NULL AND purchase_date >= '{}' AND purchase_date <= '{}'".format(start_date, end_date)
        labels2.extend(fetch_all(sql, DB))

        sql = "SELECT SUM(price) AS v FROM flight NATURAL JOIN purchases WHERE booking_agent_id IS NULL AND purchase_date >= '{}' AND purchase_date <= '{}'".format(start_date, end_date)
        labels2.extend(fetch_all(sql, DB))
        print(labels2)

        # view reports last year
        end_date = datetime.date.today()
        start_date = end_date - timedelta(days=365)
        sql = "SELECT COUNT(ticket_id) AS amount FROM purchases WHERE purchase_date >= '{}' AND purchase_date <= '{}'".format(start_date, end_date)
        report_year = fetch_all(sql, DB)
        print('report-year', report_year)

        # view reports last month
        end_date = datetime.date.today()
        start_date = end_date - timedelta(days=30)
        sql = "SELECT COUNT(ticket_id) AS amount FROM purchases WHERE purchase_date >= '{}' AND purchase_date <= '{}'".format(start_date, end_date)
        report_month = fetch_all(sql, DB)
        print('report-month', report_month)

        # month-wise
        end_date = datetime.date.today()
        start_date = end_date - timedelta(days=365)
        sql = "SELECT COUNT(ticket_id) AS v, MONTH(purchase_date) AS m FROM purchases WHERE purchase_date >= '{}' AND purchase_date <= '{}' GROUP BY MONTH(purchase_date)".format(start_date, end_date)
        labels1 = fetch_all(sql, DB)
        print('report-labels1', labels1)

        # view my flights
        start_date = datetime.date.today()
        end_date = end_date + timedelta(days=30)
        sql = "SELECT * FROM flight WHERE airline_name = '{}' AND DATE(departure_time) >= '{}' AND DATE(departure_time) <= '{}'".format(staff_airline['airline_name'], start_date, end_date)
        my_flights = fetch_all(sql, DB)
        print(my_flights)

        # view my flights
        if source_city:
            sql="SELECT * FROM flight WHERE departure_city = '{}' AND arrival_city = '{}'" \
              " AND DATE(departure_time) = '{}' AND airline_name = '{}'".format(source_city, destination_city, city_date, staff_airline['airline_name'])
            print(sql)
            flights1 = fetch_all(sql, DB)
            print('source city', flights1)
            return render_template("staff_home.html", username=session['user'], agent_ticket=agent_ticket, agent_ticket_month=agent_ticket_month,
                               agent_commission=agent_commission,
                               frequent_customer=frequent_customer, top_destinations1=top_destinations1,
                               top_destinations2=top_destinations2, labels2=labels2, report_year=report_year,
                               report_month=report_month, labels1=labels1, my_flights=my_flights, flights1=flights1, my_flights1=my_flights)

        if source_airport:
            sql="SELECT * FROM flight WHERE departure_airport = '{}' AND arrival_airport = '{}'" \
              " AND DATE(departure_time) = '{}' AND airline_name = '{}'".format(source_airport, destination_airport, airport_date, staff_airline['airline_name'])
            print(sql)
            flights1 = fetch_all(sql, DB)
            print('source airport', flights1)
            return render_template("staff_home.html", username=session['user'], agent_ticket=agent_ticket, agent_ticket_month=agent_ticket_month,
                               agent_commission=agent_commission,
                               frequent_customer=frequent_customer, top_destinations1=top_destinations1,
                               top_destinations2=top_destinations2, labels2=labels2, report_year=report_year,
                               report_month=report_month, labels1=labels1, my_flights=my_flights, flights1=flights1, my_flights1=my_flights)

        if flight_number1:
            sql = "SELECT purchases.customer_email AS c FROM flight NATURAL JOIN ticket NATURAL JOIN purchases WHERE " \
                  "flight.flight_num = '{}' AND flight.airline_name = '{}'".format(flight_number1, staff_airline['airline_name'])
            print(sql)
            flight_customers = fetch_all(sql, DB)
            print('airline_name1', flight_customers)
            return render_template("staff_home.html", username=session['user'], agent_ticket=agent_ticket, agent_ticket_month=agent_ticket_month,
                               agent_commission=agent_commission,
                               frequent_customer=frequent_customer, top_destinations1=top_destinations1,
                               top_destinations2=top_destinations2, labels2=labels2, report_year=report_year,
                               report_month=report_month, labels1=labels1, my_flights=my_flights, flight_customers=flight_customers, my_flights1=my_flights)

        if flight_from_date:
            sql = "SELECT * FROM flight WHERE departure_time >= '{}' AND departure_time <= '{}' AND airline_name = '{}'".format(flight_from_date, flight_to_date, staff_airline['airline_name'])
            print(sql)
            flights1 = fetch_all(sql, DB)
            print('flight from date', flights1)
            return render_template("staff_home.html", username=session['user'], agent_ticket=agent_ticket, agent_ticket_month=agent_ticket_month,
                               agent_commission=agent_commission,
                               frequent_customer=frequent_customer, top_destinations1=top_destinations1,
                               top_destinations2=top_destinations2, labels2=labels2, report_year=report_year,
                               report_month=report_month, labels1=labels1, my_flights=my_flights, flights1=flights1, my_flights1=my_flights)

        # create new flights
        if airline_name:
            sql = "INSERT INTO flight VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(
                airline_name, flight_number, departure_airport, departure_time, arrival_airport, arrival_time, price, status, airplane_id, departure_city, arrival_city)
            print(sql)
            result = query_mod(sql, DB)
            if result == 1:
                flash('Request denied, please try again!')
            return render_template('staff_home.html', username=session['user'], agent_ticket=agent_ticket, agent_ticket_month=agent_ticket_month, agent_commission=agent_commission,
                                   frequent_customer=frequent_customer, top_destinations1=top_destinations1, top_destinations2=top_destinations2, labels2=labels2, report_year=report_year, report_month=report_month, labels1=labels1, my_flights=my_flights, my_flights1=my_flights)

        # change status of flights
        if status_source_airport:
            sql = "UPDATE flight SET status='{}' WHERE airline_name = '{}' AND flight_num = '{}'".format(change_status, status_source_city, status_source_airport)
            print(sql)
            query_mod(sql, DB)
            return render_template('staff_home.html', username=session['user'], agent_ticket=agent_ticket, agent_ticket_month=agent_ticket_month, agent_commission=agent_commission,
                                   frequent_customer=frequent_customer, top_destinations1=top_destinations1, top_destinations2=top_destinations2, labels2=labels2, report_year=report_year, report_month=report_month, labels1=labels1, my_flights=my_flights, my_flights1=my_flights)

        # add airplane in the system
        if airline_name_plane:
            sql = "INSERT INTO airplane VALUES('{}', '{}', '{}')".format(airline_name_plane, airplane_id_plane, seat)
            print(sql)
            result = query_mod(sql, DB)
            if result == 1:
                flash('Request denied, please try again!')
            sql = "SELECT * FROM airplane WHERE airline_name = '{}'".format(airline_name_plane)
            print(sql)
            airplanes = fetch_all(sql, DB)
            print(airplanes)
            return render_template('staff_confirmation.html', username=session['user'], airplanes=airplanes, agent_ticket=agent_ticket, agent_ticket_month=agent_ticket_month,
                                   agent_commission=agent_commission, frequent_customer=frequent_customer, top_destinations1=top_destinations1, top_destinations2=top_destinations2, labels2=labels2, report_year=report_year, report_month=report_month, labels1=labels1, my_flights=my_flights, my_flights1=my_flights)

        # add new airport in the system
        if airport_name:
            sql = "INSERT INTO airport VALUES('{}', '{}')".format(airport_name, airport_city)
            print(sql)
            result = query_mod(sql, DB)
            if result == 1:
                flash('Request denied, please try again!')
            return render_template('staff_home.html', username=session['user'], agent_ticket=agent_ticket, agent_commission=agent_commission, agent_ticket_month=agent_ticket_month,
                                   frequent_customer=frequent_customer, top_destinations1=top_destinations1, top_destinations2=top_destinations2, labels2=labels2, report_year=report_year, report_month=report_month, labels1=labels1, my_flights=my_flights, my_flights1=my_flights)

        # search particular customer and airline
        if freq_customer_email:
            sql = "SELECT * FROM flight NATURAL JOIN ticket NATURAL JOIN purchases WHERE customer_email = '{}' AND flight.airline_name = '{}'".format(freq_customer_email, staff_airline['airline_name'])
            print(sql)
            flights2 = fetch_all(sql, DB)
            print(flights2)
            return render_template('staff_home.html', username=session['user'], agent_ticket=agent_ticket, agent_commission=agent_commission, agent_ticket_month=agent_ticket_month,
                                   frequent_customer=frequent_customer, flights2=flights2, top_destinations1=top_destinations1, top_destinations2=top_destinations2, labels2=labels2, report_year=report_year, report_month=report_month, labels1=labels1, my_flights=my_flights, my_flights1=my_flights)

        # view reports custom dates
        if report_to_date:
            sql = "SELECT COUNT(ticket_id) AS amount FROM purchases WHERE purchase_date >= '{}' AND purchase_date <= '{}'".format(report_from_date, report_to_date)
            print(sql)
            report_custom = fetch_all(sql, DB)
            print('report-custom', report_custom)
            return render_template('staff_home.html', username=session['user'], agent_ticket=agent_ticket, agent_commission=agent_commission, agent_ticket_month=agent_ticket_month,
                                   frequent_customer=frequent_customer, top_destinations1=top_destinations1, top_destinations2=top_destinations2, labels2=labels2, report_year=report_year, report_month=report_month, report_custom=report_custom, labels1=labels1, my_flights=my_flights, my_flights1=my_flights)

        return render_template("staff_home.html", username = session['user'], agent_ticket=agent_ticket, agent_commission=agent_commission, agent_ticket_month=agent_ticket_month,
                               frequent_customer=frequent_customer, top_destinations1=top_destinations1, top_destinations2=top_destinations2, labels2=labels2, report_year=report_year, report_month=report_month, labels1=labels1, my_flights=my_flights, my_flights1=my_flights)
    return redirect(url_for('home_page_get'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


@app.errorhandler(405)
def request_error(e):
    return render_template('405.html')

@app.errorhandler(500)
def server_wrong(e):
    return render_template('500.html')

@app.route('/login/', methods = ['GET', 'POST'])
def login_page():
    return render_template("login.html")


@app.route('/login-customer/', methods = ['GET', 'POST'])
def login_customer():
    try:
        if request.method == "POST":
            session.pop('user', None)
            session.pop('type', None)
            email = replace(request.form['email'])
            # Password encoded with utf-8 first then encoded with md5
            password = md5(replace(request.form['password']).encode('utf-8')).hexdigest()
            sql = 'SELECT password FROM customer WHERE email = "{}"'.format(email)
            db_pwd = query_fetch(sql, DB)
            if db_pwd is None:
                err = "Account does not exist"
                flash(err)
            elif password == db_pwd['password']:
                session['user'] = email
                session['type'] = 'customer'
                print(session['user'])
                print(session['type'])
                return redirect(url_for('customer_page'))
            else:
                err = "Password error!"
                flash(err)
        return render_template("login1.html")

    except Exception as e:
        flash(str(e))
        return render_template("login1.html")


@app.route('/login-agent/', methods = ['GET', 'POST'])
def login_agent():
    try:
        if request.method == "POST":
            session.pop('user', None)
            session.pop('type', None)
            email = replace(request.form['email'])
            # Password encoded with utf-8 first then encoded with md5
            password = md5(replace(request.form['password']).encode('utf-8')).hexdigest()
            sql = 'SELECT password FROM booking_agent WHERE email = "{}"'.format(email)
            db_pwd = query_fetch(sql, DB)
            if db_pwd is None:
                err = "Account does not exist"
                flash(err)
            elif password == db_pwd['password']:
                session['user'] = email
                session['type'] = 'agent'
                print(session['user'])
                print(session['type'])
                return redirect(url_for('agent_page'))

            else:
                err = "Password error!"
                flash(err)
        return render_template("login2.html")

    except Exception as e:
        flash(str(e))
        return render_template("login2.html")


@app.route('/login-staff/', methods = ['GET', 'POST'])
def login_staff():
    try:
        if request.method == "POST":
            session.pop('user', None)
            session.pop('type', None)
            username = request.form['username']
            # Password encoded with utf-8 first then encoded with md5
            password = md5(request.form['password'].encode('utf-8')).hexdigest()
            sql = 'SELECT password FROM airline_staff WHERE username = "{}"'.format(username)
            db_pwd = query_fetch(sql, DB)
            if db_pwd is None:
                err = "Account does not exist"
                flash(err)
            elif password == db_pwd['password']:
                session['user'] = username
                session['type'] = 'staff'
                print(session['user'])
                print(session['type'])
                return redirect(url_for('staff_page'))
            else:
                err = "Password error!"
                flash(err)
        return render_template("login3.html")

    except Exception as e:
        flash(str(e))
        return render_template("login3.html")


@app.route('/register/', methods = ['GET', 'POST'])
def register_page():
    return render_template("register.html")


@app.route('/register-customer/', methods = ['GET', 'POST'])
def register_customer():
    try:
        if request.method == "POST":
            email = replace(request.form['email'])
            name = replace(request.form['name'])
            pwd = replace(request.form['password'])
            confirm_pwd = replace(request.form['confirm_password'])
            if pwd != confirm_pwd:
                err = "password and confirm password doesn't match!"
                flash(err)
                return render_template("form1.html")
            # Password encoded with utf-8 first then encoded with md5
            password = md5(replace(request.form['password']).encode('utf-8')).hexdigest()
            building_number = replace(request.form['building_number'])
            street = replace(request.form['street'])
            city = replace(request.form['city'])
            state = replace(request.form['state'])
            phone_number = replace(request.form['phone_number'])
            passport_number = replace(request.form['passport_number'])
            passport_expiration = replace(request.form['passport_expiration'])
            passport_country = replace(request.form['passport_country'])
            date_of_birth = replace(request.form['date_of_birth'])
            sql_check = 'SELECT * FROM customer WHERE email = "{}"'.format(email)
            user_exist = query_fetch(sql_check, DB)
            if user_exist is not None:
                err = "User already exists!"
                flash(err)
            else:
                sql_add = 'INSERT INTO customer VALUES("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", ' \
                            '"{}", "{}")'.format(email, name, password, building_number, street, city, state, phone_number,
                                                 passport_number, passport_expiration, passport_country, date_of_birth)
                result = query_mod(sql_add, DB)
                if result == 1:
                    flash('Request denied, please try again!')
                session['user'] = email
                session['type'] = 'customer'
                print(session['user'])
                print(session['type'])
                return redirect(url_for('customer_page'))
        return render_template("form1.html")

    except Exception as e:
        flash(str(e))
        return render_template("form1.html")


@app.route('/register-agent/', methods = ['GET', 'POST'])
def register_agent():
    try:
        if request.method == "POST":
            email = replace(request.form['email'])
            pwd = replace(request.form['password'])
            confirm_pwd = replace(request.form['confirm_password'])
            if pwd != confirm_pwd:
                err = "password and confirm password doesn't match!"
                flash(err)
                return render_template("form2.html")
            # Password encoded with utf-8 first then encoded with md5
            password = md5(replace(request.form['password']).encode('utf-8')).hexdigest()
            booking_agent_id = replace(request.form['booking_agent_id'])
            sql_check = 'SELECT * FROM booking_agent WHERE email = "{}"'.format(email)
            user_exist = query_fetch(sql_check, DB)
            if user_exist is not None:
                err = "User already exists!"
                flash(err)
            else:
                sql_add = 'INSERT INTO booking_agent VALUES("{}", "{}", "{}")'.format(email, password, booking_agent_id)
                result = query_mod(sql_add, DB)
                if result == 1:
                    flash('Request denied, please try again!')
                session['user'] = email
                session['type'] = 'agent'
                print(session['user'])
                print(session['type'])
                return redirect(url_for('agent_page'))
        return render_template("form2.html")

    except Exception as e:
        flash(str(e))
        return render_template("form2.html")


@app.route('/register-staff/', methods = ['GET', 'POST'])
def register_staff():
    try:
        if request.method == "POST":
            username = replace(request.form['username'])
            pwd = replace(request.form['password'])
            confirm_pwd = replace(request.form['confirm_password'])
            if pwd != confirm_pwd:
                err = "password and confirm password doesn't match!"
                flash(err)
                return render_template("form3.html")
            # Password encoded with utf-8 first then encoded with md5
            password = md5(replace(request.form['password']).encode('utf-8')).hexdigest()
            first_name = replace(request.form['first_name'])
            last_name = replace(request.form['last_name'])
            date_of_birth = replace(request.form['date_of_birth'])
            airline_name = replace(request.form['airline_name'])

            sql_check = 'SELECT * FROM airline_staff WHERE username = "{}"'.format(username)
            user_exist = query_fetch(sql_check, DB)
            if user_exist is not None:
                err = "User already exists!"
                flash(err)
            else:
                sql_add = 'INSERT INTO airline_staff VALUES("{}", "{}", "{}", "{}", "{}", "{}")'.format(
                    username, password, first_name, last_name, date_of_birth, airline_name)
                result = query_mod(sql_add, DB)
                if result == 1:
                    flash('Request denied, please try again!')
                session['user'] = username
                session['type'] = 'staff'
                print(session['user'])
                print(session['type'])
                return redirect(url_for('staff_page'))
        return render_template("form3.html")

    except Exception as e:
        flash(str(e))
        return render_template("form3.html")


@app.route('/logout/', methods = ['GET', 'POST'])
def logout_redirect():
    print(session['user'])
    print(session['type'])
    session.pop('user', None)
    session.pop('type', None)
    return redirect(url_for('login_page'))


@app.before_request
def before_request():
    g.user = None
    g.type = None
    if 'user' in session:
        g.user = session['user']
    if 'type' in session:
        g.type = session['type']


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
