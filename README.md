# Aureum

Aureum is a FastAPI-based project that implements user authentication and integrates with MongoDB.

## Features

- User model implementation
- Authentication system
- MongoDB integration
- FastAPI framework

## Requirements

- Python 3.7+
- FastAPI
- MongoDB
- PyMongo (for MongoDB interaction)
- Python-jose (for JWT token handling)
- Passlib (for password hashing)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/sourabhraikwar/aureum.git
   cd aureum
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Configuration

1. Set up your MongoDB database.
2. Create a `.env` file in the project root and add your configuration:
   ```
   MONGODB_URL=your_mongodb_connection_string
   SECRET_KEY=your_secret_key_for_jwt
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

## Usage

1. Start the server:
   ```
   uvicorn app.main:app --reload
   ```

2. Open your browser and go to `http://127.0.0.1:8000/docs` to see the Swagger UI documentation and test the API endpoints.

## Project Structure

```
aureum/
├── app/
│   ├── auth/
│   │   ├── __init__.py
│   │   └── jwt_handler.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── user_model.py
│   ├── routes/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── user_schema.py
│   └── main.py
├── .env
├── .gitignore
├── README.md
└── requirements.txt
```

## API Endpoints

- `POST /user/signup`: Create a new user
- `POST /user/login`: Authenticate a user and receive a token
- `GET /user/me`: Get current user details (requires authentication)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open-source. Please check the repository for license information.