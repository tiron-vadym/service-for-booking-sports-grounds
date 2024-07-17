# SportSpace

Service for booking sports grounds written on DRF

## Check it out!

[SportSpace API deployed to Render](https://sportspace.onrender.com/)

[SportSpace project with frontend deployed to Vercel](https://sport-space.vercel.app/)

## Installing using GitHub

Install PostgresSQL and create db

```shell
git clone https://github.com/tiron-vadym/service-for-booking-sports-grounds
cd sports_sports_API
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
set DB_HOST=<your db hostname>
set DB_NAME=<your db name>
set DB_USER=<your db username>
set DB_PASSWORD=<your db user password>
set SECRET_KEY=<your secret key>
python manage.py migrate
python manage.py runserver
```

## Endpoints

- Admin Panel: `/admin/`

## Debugging and Documentation

- Debug Toolbar: `/__debug__/`
- API Schema: `/schema/`
- Swagger Documentation: `/api/doc/swagger/`
- ReDoc Documentation: `/api/doc/redoc/`

## Client Endpoints
Register: `/api/client/register/`
User Details: `/api/client/me/`
User Schedule: `/api/client/me/schedule/`
Change Password: `/api/client/me/password/`
List Users: `/api/client/users/`
Get Token: `/api/client/token/`
Refresh Token: `/api/client/token/refresh/`
Verify Token: `/api/client/token/verify/`
Logout: `/api/client/logout/`

## Service Endpoints
Sports Complexes: `/api/service/sports-complexes/`
Upload image: `/api/service/sports-complexes/upload_image`
Sports Fields: `/api/service/sports-fields/`
Sports Fields's booking: `/api/service/sports-fields/booking`
Bookings: `/api/service/bookings/`
Payments: `/api/service/payments/`
FAQ: `/api/about/faq/`
Feedback: `/api/about/feedbacks`