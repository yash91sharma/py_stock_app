from flask import render_template, url_for, flash, redirect, request
from stockapp import app, db, bcrypt, mail
from stockapp.forms import (RegistrationForm,
                            LoginForm,
                            RequestResetForm,
                            ResetPasswordForm)
from stockapp.models import User
from flask_login import login_user, current_user, logout_user, login_required
from stockapp import stock_fc, _user_view, _stock_list, _n_days, _color_pallet
import pandas as pd
import numpy as np
from flask_mail import Message


@app.route('/')
@app.route('/home')
def home():
    global _user_view
    global _stock_list
    _user_view = 'home'
    returns, num_stocks = stock_fc.get_summary(_stock_list)
    return render_template('home.html',title='Home',
                           total_returns=returns,
                           num_stocks=num_stocks)

@app.route('/opportunity')
@login_required
def opportunity():
    global _user_view
    global _stock_list
    df = stock_fc.agg_data_by_x(_stock_list, 'ticker', None)
    df['price_diff'] = df['unit_price'] - df['close_price']
    df['price_diff_color'] = ['mediumseagreen' if x > 0 else 'orange' for x in df['price_diff']]
    df.sort_values(by=['price_diff'], ascending=False, inplace=True, ignore_index=True)
    return render_template('opportunity.html', title = 'Buying Opportunity',
                           stock_price_diff = df['price_diff'].round(2).tolist(),
                           stock_label = df['ticker'].tolist(),
                           stock_color = df['price_diff_color'].tolist())

@app.route('/past_dividends')
@login_required
def past_dividends():
    global _user_view
    global _stock_list
    global _color_pallet
    _user_view = 'past_dividends'
    #get dividend earned
    dividend_yield = stock_fc.get_dividend_yields(_stock_list)
    df = stock_fc.agg_data_by_x(_stock_list, 'ticker', 365)
    df = df.merge(dividend_yield, how='left', left_on='ticker', right_on='ticker')
    df['units_times_dividend_yield'] = df['dividend_yield'] * df['qty']
    df.sort_values(by=['sector','ticker'], inplace=True, ignore_index=True)
    #get dividends by stock
    stock_list = df['ticker'].unique().tolist()
    stock_dividend_yield = []
    for i in stock_list:
        df_temp = df[df['ticker'] == i]
        stock_dividend_yield.append(sum(df_temp['units_times_dividend_yield'])/sum(df_temp['qty']))
    #get dividends by sector
    sector_list = df['sector'].unique().tolist()
    sector_dividend_yield = []
    for i in sector_list:
        df_temp = df[df['sector'] == i]
        sector_dividend_yield.append(sum(df_temp['units_times_dividend_yield'])/sum(df_temp['qty']))
    #get expected dividend
    future_dividend_by_value, future_dividend_by_yield = stock_fc.get_future_dividend(_stock_list)
    return render_template('past_dividends.html',title='Past Dividends',
                           dividends_earned = stock_fc.get_past_dividends_agg(_stock_list),
                           future_dividend_by_value = future_dividend_by_value,
                           future_dividend_by_yield = future_dividend_by_yield,
                           overall_dividend_yield = sum(df['units_times_dividend_yield'])/sum(df['qty']),
                           sector_list = sector_list,
                           sector_dividend_yield = list(np.around(np.array(sector_dividend_yield),2)),
                           color_pallet = _color_pallet,
                           stock_list = stock_list,
                           stock_dividend_yield = list(np.around(np.array(stock_dividend_yield),2)))

@app.route('/sector')
@login_required
def sector():
    global _user_view
    global _stock_list
    global _color_pallet
    _user_view = 'sector'
    #For doughnut and radar charts
    df = stock_fc.agg_data_by_x(_stock_list, 'ticker', None)
    df_sector = df.groupby(['sector']).agg({'ttl_investment':'sum','ttl_value':'sum'}).reset_index()
    df_sector['returns'] = 100*(df_sector['ttl_value'] - df_sector['ttl_investment'])/df_sector['ttl_investment']
    df_sector['sector_invest_perc'] = 100*(df_sector['ttl_value'])/sum(df_sector['ttl_value'])
    df_sector.sort_values(by=['sector'], inplace=True, ignore_index=True)
    #For sector growth by time
    df = stock_fc.agg_data_by_x(_stock_list, 'sector_record_date', 365)
    df.sort_values(by=['sector','record_date'], inplace=True, ignore_index = True)
    df['returns'] = 100*(df['ttl_value']-df['ttl_investment'])/df['ttl_investment']
    df = df.fillna(0)
    chart2_sector_names = df['sector'].unique().tolist()
    chart2_sector_value = []
    chart2_sector_returns = []
    for sector in chart2_sector_names:
        df_temp = df[df['sector'] == sector]
        chart2_sector_value.append(df_temp['ttl_value'].round(0).tolist())
        chart2_sector_returns.append(df_temp['returns'].round(2).tolist())
    return render_template("sector.html",
                           title="Sector View",
                           chart_sector_value = df_sector['ttl_value'].round(0).tolist(),
                           chart_sector_label = df_sector['sector'].astype(str).tolist(),
                           chart_sector_returns = df_sector['returns'].round(0).tolist(),
                           chart_sector_invest_perc = df_sector['sector_invest_perc'].round(0).tolist(),
                           color_pallet = _color_pallet,
                           chart2_sector_label = df['record_date'].unique().astype(str).tolist(),
                           chart2_sector_value_data = zip(chart2_sector_value, chart2_sector_names, _color_pallet),
                           chart2_sector_return_data = zip(chart2_sector_returns, chart2_sector_names, _color_pallet))

@app.route('/growth')
@login_required
def growth():
    global _user_view
    global _stock_list
    global _n_days
    _user_view = 'growth'
    df = stock_fc.agg_data_by_x(_stock_list, 'record_date', _n_days)
    # print(_n_days, type(_n_days))
    df['daily_return_perc'] = 100*(df['ttl_value'] - df['ttl_investment'])/df['ttl_investment']
    df['return_color'] = ['mediumseagreen' if x > 0 else 'orange' for x in df['daily_return_perc']]
    return render_template("growth.html",
                           title = 'Growth over time',
                           chart_portfolio_value = df['ttl_value'].round(0).tolist(),
                           chart_invested_value = df['ttl_investment'].round(0).tolist(),
                           chart_return_value = df['daily_return_perc'].round(2).tolist(),
                           chart_return_value_color = df['return_color'].astype(str).tolist(),
                           chart_label = df['record_date'].astype(str).tolist())

@app.route('/test_app')
def test_app():
    return render_template('test_app.html', title='Test Application Integrity')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('Already logged in.', 'success')
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data,
                    email=form.email.data,
                    password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}', 'success')
        return redirect(url_for('login'))
    return render_template('register.html',title = 'Register',form = form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('Already logged in.', 'success')
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Login success!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Bad login!', 'danger')
    return render_template('login.html',title = 'Login',form = form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/account')
@login_required
def account():
    image_file = url_for('static',filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file)

@app.route('/filters', methods=['GET', 'POST'])
@login_required
def filters():
    global _user_view
    global _stock_list
    global _n_days
    stock_list, sector_list = stock_fc.get_sector_stock_list()
    if request.method == 'POST':
        user_inputs = request.form.getlist('checkbox_sector') + request.form.getlist('checkbox_stock')
        _stock_list = stock_fc.get_stock_list(user_inputs)
        _n_days = stock_fc.get_days_from_user_input(request.form.get('timeframe'))
        return redirect(url_for(_user_view))
    return render_template('filters.html',
                           title='Filter Stocks',
                           sector_list = sector_list,
                           stock_list = stock_list)

@app.route('/update_stock_data', methods=['GET', 'POST'])
@login_required
def update_stock_data():
    global _user_view
    if request.method == 'POST':
        stock_fc.update_daily_snapshot()
        stock_fc.update_dividend_yields_records()
        flash('Records synced up with latest market data!', 'success')
        return redirect(url_for(_user_view))
    return render_template('update_stock_data.html',
                           title='Update Stock Data')

@app.route('/update_transaction', methods=['GET', 'POST'])
@login_required
def update_transaction():
    if request.method == 'POST':
        file = request.files['file']
        if (file.filename).endswith('csv'):
            df = pd.read_csv(file)
            print(df.shape)
            stock_fc.update_m1_txn_database(df,'Trade Date','Symbol','Quantity','Buy/Sell','Unit Price')
            flash('Transactions updated.', 'success')
        else:
            flash('Invalid file type. CSV required.', 'danger')
    return render_template('update_transaction.html',
                           title='Add M1 Transaction')

@app.route('/update_transaction_manual', methods=['GET', 'POST'])
@login_required
def update_transaction_manual():
    if request.method == 'POST':
        try:
            ticker = request.form['ticker']
            txn_date = request.form['txn_date']
            txn_type = request.form['txn_type']
            stock_price = float(request.form['stock_price'])
            qty = float(request.form['qty'])
            print(txn_date)
            print(type(txn_date))
            stock_fc.add_manual_transaction(ticker, txn_date, txn_type, stock_price, qty)
            flash('Success!', 'success')
        except:
            flash('Invalid values!', 'danger')
    return render_template('update_transaction_manual.html',
                           title='Add Manual Transaction')

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender = 'yash91sharma.bot@gmail.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request, then please ignore this email.
'''
    mail.send(msg)

@app.route('/reset_request', methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        flash('Already logged in.', 'success')
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Reset email sent!', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title="Reset Password",
                           form = form)

@app.route('/reset_password/<token>', methods=['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        flash('Already logged in.', 'success')
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Invalid or expired token', 'danger')
        return redirect(url_for('reset_password'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'Password updated!', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title="Reset Password",
                           form = form)

@app.route('/research', methods=['GET','POST'])
@login_required
def research():
    global _user_view
    global _n_days
    _user_view = 'research'
    if request.method == 'POST':
        ticker = request.form.get('ticker')
        df = stock_fc.research_data(ticker, _n_days)
        return render_template('research.html', title='Stock Research',
                               graph_flag = True,
                               close_price = df['close_price'].round(2).tolist(),
                               record_date = df['record_date'].astype(str).tolist(),
                               sma50 = df['close_price_sma50'].round(2).tolist(),
                               sma200 = df['close_price_sma200'].round(2).tolist(),
                               ticker = ticker)
    return render_template('research.html', title='Stock Research',
                           graph_flag = False)
