# Railway Reservation System

A comprehensive web-based railway ticket booking and management system built with Flask and MySQL. This system allows users to search for trains, book tickets, manage reservations, and provides administrators with tools to manage trains, schedules, and system operations.

## 🚀 Features

### For Passengers
- **User Registration & Authentication**: Secure user accounts with role-based access
- **Train Search**: Search trains by route, date, and preferences
- **Ticket Booking**: Book tickets with seat selection and passenger details
- **Booking Management**: View, modify, and cancel bookings
- **Payment Processing**: Integrated payment system for ticket purchases
- **PNR Management**: Track bookings using PNR numbers

### For Administrators
- **Train Management**: Add, edit, and delete train information
- **Schedule Management**: Manage train schedules and routes
- **Class Configuration**: Configure train classes (AC, Sleeper, General) with pricing
- **Seat Availability**: Monitor and manage seat availability
- **User Management**: Oversee user accounts and permissions
- **System Monitoring**: Track train status and system performance

## 🛠 Technology Stack

- **Backend**: Python Flask
- **Database**: MySQL
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: Flask-Session with role-based access control
- **Database Connector**: MySQL Connector Python
- **Environment Management**: python-dotenv

## 📋 Prerequisites

- Python 3.8 or higher
- MySQL Server 8.0 or higher
- pip (Python package manager)

## 🔧 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd railway-reservation-system
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup

#### Create Database
```sql
-- Run the SQL script to create database and tables
mysql -u root -p < Railway_DataBase.sql
```

#### Configure Environment Variables
Create a `.env` file in the root directory:
```env
# MySQL Configuration
DB_HOST=127.0.0.1
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=railway_system
DB_PORT=3306

# Admin Credentials
ADMIN_EMAIL=admin@gmail.com
ADMIN_PASSWORD=adminpass

# Flask Secret Key
FLASK_SECRET_KEY=your_secret_key_here
```

### 5. Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 📊 Database Schema

The system uses a comprehensive MySQL database with the following main tables:

- **user**: User accounts and profiles
- **station**: Railway station information
- **route**: Train route definitions
- **route_station**: Route-station mappings with timings
- **train**: Train information and configurations
- **schedule**: Train schedule details
- **class**: Train class configurations (AC, Sleeper, etc.)
- **ticket**: Booking information
- **passenger**: Passenger details for bookings
- **payment**: Payment transaction records
- **cancellation**: Cancellation records

## 🎯 Usage

### User Registration
1. Visit the registration page
2. Fill in personal details (name, email, password, etc.)
3. Verify account and login

### Searching Trains
1. Use the search functionality on the homepage
2. Enter source, destination, and travel date
3. View available trains with schedules and fares

### Booking Tickets
1. Select a train from search results
2. Choose travel class and number of passengers
3. Enter passenger details
4. Complete payment to confirm booking

### Admin Operations
1. Login with admin credentials
2. Access admin dashboard
3. Manage trains: Add/Edit/Delete train information
4. Configure schedules and routes
5. Monitor system status

## 📁 Project Structure

```
railway-reservation-system/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── Railway_DataBase.sql        # Database schema
├── .env                       # Environment configuration
├── railway_app/               # Alternative app structure
│   ├── app.py
│   ├── requirements.txt
│   └── templates/
├── templates/                 # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── search_trains.html
│   ├── train_detail.html
│   ├── admin_add_train.html
│   ├── admin_edit_train.html
│   ├── admin_trains.html
│   └── ...
├── static/                    # Static assets
│   ├── style.css
│   └── ...
└── README.md
```

## 🔗 API Endpoints

### Public Endpoints
- `GET /` - Homepage
- `GET/POST /login` - User login
- `GET/POST /register` - User registration
- `GET /logout` - User logout
- `GET /search` - Train search
- `GET /train/<train_no>` - Train details

### User Endpoints (Requires Login)
- `GET /user` - User dashboard
- `POST /book/<train_no>` - Book tickets
- `GET /tickets` - View bookings
- `POST /cancel` - Cancel bookings

### Admin Endpoints (Requires Admin Role)
- `GET /admin` - Admin dashboard
- `GET /admin/trains` - Manage trains
- `GET/POST /admin/add-train` - Add new train
- `GET/POST /admin/edit-train/<train_no>` - Edit train
- `GET /admin/delete-train/<train_no>` - Delete train

## 🔐 Security Features

- **Password Hashing**: Secure password storage
- **Session Management**: Flask session-based authentication
- **Role-Based Access Control**: Different permissions for users and admins
- **Input Validation**: Form validation and sanitization
- **SQL Injection Prevention**: Parameterized queries

## 🧪 Testing

### Manual Testing Checklist
- [ ] User registration and login
- [ ] Train search functionality
- [ ] Ticket booking process
- [ ] Payment integration
- [ ] Booking cancellation
- [ ] Admin train management
- [ ] Schedule modifications
- [ ] Seat availability updates

### Database Testing
- [ ] Verify all foreign key relationships
- [ ] Test cascade delete operations
- [ ] Check data integrity constraints

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 Python style guidelines
- Write clear, concise commit messages
- Test all changes thoroughly
- Update documentation as needed

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Your Name** - *Initial work* - [Your GitHub](https://github.com/yourusername)

## 🙏 Acknowledgments

- Flask framework for the web application
- MySQL for database management
- Bootstrap/CSS frameworks for UI styling
- Open source community for various libraries and tools

## 📞 Support

For support, email support@railway-system.com or create an issue in the repository.

---

**Note**: This is a mini-project for educational purposes. For production use, additional security measures, testing, and scalability considerations would be required.
