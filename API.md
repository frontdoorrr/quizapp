# Quiz App API Documentation

## Authentication
All endpoints except `/user/login` require JWT authentication. Include the JWT token in the Authorization header:
```
Authorization: Bearer <token>
```

## User Management

### Login
- **URL**: `/user/login`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "email": "string",
    "password": "string"
  }
  ```
- **Success Response**: `200 OK`
  ```json
  {
    "access_token": "string",
    "token_type": "bearer"
  }
  ```
- **Error Response**: `401 Unauthorized`

### Create User
- **URL**: `/user`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "email": "string",
    "password": "string",
    "name": "string",
    "phone": "string",
    "nickname": "string"
  }
  ```
- **Success Response**: `201 Created`
  ```json
  {
    "id": "string",
    "email": "string",
    "name": "string",
    "phone": "string",
    "nickname": "string",
    "point": 0,
    "coin": 0,
    "created_at": "datetime",
    "updated_at": "datetime"
  }
  ```
- **Error Response**: `400 Bad Request` if email already exists

### Get User List
- **URL**: `/user`
- **Method**: `GET`
- **Query Parameters**:
  - `order`: string (asc/desc) - Sort by creation date
- **Success Response**: `200 OK`
  ```json
  [
    {
      "id": "string",
      "email": "string",
      "name": "string",
      "phone": "string",
      "nickname": "string",
      "point": 0,
      "coin": 0,
      "created_at": "datetime",
      "updated_at": "datetime"
    }
  ]
  ```

## Game Management

### Create Game
- **URL**: `/game`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "question": "string",
    "answer": "string",
    "category": "string"
  }
  ```
- **Success Response**: `201 Created`
  ```json
  {
    "id": "string",
    "question": "string",
    "answer": "string",
    "category": "string",
    "created_at": "datetime",
    "updated_at": "datetime"
  }
  ```

### Get Game List
- **URL**: `/game`
- **Method**: `GET`
- **Query Parameters**:
  - `category`: string (optional) - Filter by category
- **Success Response**: `200 OK`
  ```json
  [
    {
      "id": "string",
      "question": "string",
      "answer": "string",
      "category": "string",
      "created_at": "datetime",
      "updated_at": "datetime"
    }
  ]
  ```

## Answer Management

### Submit Answer
- **URL**: `/answer`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "game_id": "string",
    "answer": "string"
  }
  ```
- **Success Response**: `200 OK`
  ```json
  {
    "id": "string",
    "game_id": "string",
    "user_id": "string",
    "answer": "string",
    "is_correct": boolean,
    "solved_at": "datetime",
    "created_at": "datetime",
    "updated_at": "datetime",
    "point": integer
  }
  ```
- **Error Responses**:
  - `404 Not Found`: Game not found
  - `422 Unprocessable Entity`: Insufficient coins to submit answer

### Get Answer by ID
- **URL**: `/answer/{answer_id}`
- **Method**: `GET`
- **Success Response**: `200 OK`
  ```json
  {
    "id": "string",
    "game_id": "string",
    "user_id": "string",
    "answer": "string",
    "is_correct": boolean,
    "solved_at": "datetime",
    "created_at": "datetime",
    "updated_at": "datetime",
    "point": integer
  }
  ```
- **Error Response**: `404 Not Found`

### Get Answers by Game
- **URL**: `/answer/game/{game_id}`
- **Method**: `GET`
- **Success Response**: `200 OK`
  ```json
  [
    {
      "id": "string",
      "game_id": "string",
      "user_id": "string",
      "answer": "string",
      "is_correct": boolean,
      "solved_at": "datetime",
      "created_at": "datetime",
      "updated_at": "datetime",
      "point": integer
    }
  ]
  ```

### Get Answers by User
- **URL**: `/answer/user/{user_id}`
- **Method**: `GET`
- **Success Response**: `200 OK`
  ```json
  [
    {
      "id": "string",
      "game_id": "string",
      "user_id": "string",
      "answer": "string",
      "is_correct": boolean,
      "solved_at": "datetime",
      "created_at": "datetime",
      "updated_at": "datetime",
      "point": integer
    }
  ]
  ```
- **Error Response**: `403 Forbidden` if trying to access another user's answers

## Inquiry Management

### Create Inquiry
- **URL**: `/inquiry`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "title": "string",
    "content": "string"
  }
  ```
- **Success Response**: `201 Created`
  ```json
  {
    "id": "string",
    "user_id": "string",
    "title": "string",
    "content": "string",
    "created_at": "datetime",
    "updated_at": "datetime"
  }
  ```

### Get Inquiry List
- **URL**: `/inquiry`
- **Method**: `GET`
- **Success Response**: `200 OK`
  ```json
  [
    {
      "id": "string",
      "user_id": "string",
      "title": "string",
      "content": "string",
      "created_at": "datetime",
      "updated_at": "datetime"
    }
  ]
  ```

## Business Rules

### Answer Submission
- Users must have at least 1 coin to submit an answer
- Each answer submission costs 1 coin
- Correct answers earn 10 points
- Incorrect answers earn 0 points
- The solved_at timestamp is only set when the answer is correct

### Authentication
- JWT tokens expire after 6 hours
- Only authenticated users can access protected endpoints
- Users can only view their own answers
