## Challenge 4 - Docker Compose

### **Part 1: Walkthrough**

#### **Goal:**
Students will create and run a simple `docker-compose.yml` file that sets up a multi-service application consisting of a web server (NGINX) and a database (MySQL).

---

### **Step-by-Step Walkthrough**

#### **Step 1: Introduction to `docker-compose.yml`**
Explain:
- A `docker-compose.yml` file allows you to define and run multi-container Docker applications.
- Each service in the file represents a container.

---

#### **Step 2: Writing the `docker-compose.yml`**

1. Clone and open this repo.

2. Create a file named `docker-compose.yml` and open it in a text editor.

3. Define the `web` service:

    ```yaml
    version: '3.9'  # Compose file format version

    services:
      web:
        image: nginx:latest  # Official NGINX image
        ports:
          - "8080:80"        # Maps port 80 inside the container to port 8080 on the host
        volumes:
          - ./html:/usr/share/nginx/html  # Mounts a local folder to serve HTML files

    # this should be at the very bottom
    networks:
      default:
        driver: bridge
    ```

4. Start the `web` service:

    ```bash
    docker compose up -d
    ```

5. Verify the `web` service is running:

    ```bash
    docker compose ps
    ```

6. Open a browser and navigate to `http://localhost:8080`. You should get a response page from nginx, may be a 403 forbidden

7. Add the `db` service to the `docker-compose.yml` file:

    ```yaml
    ...
      web:
        image: nginx:latest
        ports:
          - "8080:80"
        volumes:
          - ./html:/usr/share/nginx/html

      db:
        image: mysql:latest  # Official MySQL image
        environment:
          MYSQL_ROOT_PASSWORD: supersecret # Root password
          MYSQL_DATABASE: testdb # Name of the default database
          MYSQL_USER: mysqluser # Custom MySQL user
          MYSQL_PASSWORD: notsosecretpassword # Password for custom user

    # this should be at the very bottom
    networks:
      default:
        driver: bridge
    ```

8. Start the `db` service:

    ```bash
    docker compose up -d
    ```

9. Verify the containers for both services are running:

    ```bash
    docker compose ps
    ```
    
10. Now let's shut them down to see the process
    ```bash
    docker compose down
    ```

11. Add a `depends_on` keyword so that docker knows to start the database first and then the nginx webserver
    ```bash
    services:
      web:
        image: nginx:latest  # Official NGINX image
        ports:
          # Maps port 80 in the container to port 8080 on host
          - "8080:80"
        volumes:
           # Mounts a local folder to serve HTML files
          - ./html:/usr/share/nginx/html 
        depends_on: 
          - db

      db:
        image: mysql:latest  # Official MySQL image
        ...
    ```
---

#### **Step 3: Running Docker-Compose**

1. Start the services:

    ```bash
    docker compose up -d
    ```

    Explain:
    - `up` starts the services.
    - `-d` runs them in detached mode (in the background).

2. Verify the containers are running:

    ```bash
    docker compose ps
    ```

3. Open a browser and navigate to `http://localhost:8080`. The default NGINX page should appear.

4. Check the logs of a specific service:

    ```bash
    docker compose logs web
    ```

5. Stop the services when done:

    ```bash
    docker compose down
    ```

---

#### **Step 4: Customizing the Web Server**

1. Create a directory named `html` in the project folder if it doesn't already exist:

    ```bash
    mkdir html
    ```

2. Add an `index.html` file to the `html` directory:

    ```
    <!DOCTYPE html>
    <html>
    <head>
        <title>Welcome to NGINX</title>
    </head>
    <body>
        <h1>Hello from Docker-Compose!</h1>
    </body>
    </html>
    ```

3. Restart the services to load the custom HTML:

    ```bash
    docker compose up -d
    ```

4. Refresh the browser at `http://localhost:8080` to see the new page.

---

### **Part 2: Challenge**

#### **Challenge Goal:**
Students will extend the knowledge from the walkthrough to:
1. Add a Python Flask application as a new service.
2. Connect it with the existing MySQL database service.

---

#### **Challenge Steps**

1. **Setup:**

    Create a directory named `challenge` that we will use to initialize a Flask application.

2. **Create the Flask app:**

    Inside of the directory `challenge`, create a file named `app.py`:

    ```python
    from flask import Flask, jsonify
    import mysql.connector

    app = Flask(__name__)

    @app.route('/')
    def home():
        return "Welcome to the Flask App!"

    @app.route('/data')
    def data():
        connection = mysql.connector.connect(
            host="db",
            user="user",
            password="userpassword",
            database="testdb"
        )
        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE();")
        db_name = cursor.fetchone()
        return jsonify({"Connected to": db_name[0]})

    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=5000)
    ```
    **HINT**: Make sure the arguments in `mysql.connector.connect(...)` match up to the environment variables for the `db` service in your `docker-compose.yml`. Otherwise your Flask app will fail to actually authenticate with the database.

3. **Create the requirements file:**

    Inside of the `challenge` directory, create a `requirements.txt` file with this content:
    ```
    flask==2.2.5
    mysql-connector-python==8.0.33
    ```

4. **Create the Dockerfile:**  

    Inside of the `challenge` directory, create a `Dockerfile`. It should have the following requirements:
    - Base image should be `python:3.9-slim`
    - The working directory should be `/app`
    - Copy over the `requirements.txt` file to `.` inside the container
    - There should be a `RUN` statement here that executes `pip install --noc-cache-dir -r requirements.txt`
    - Copy over the current directory on the host over to `.` inside the container, i.e. after copying over and installing the dependencies in `requirements.txt` it should copy over everything else in the directory
    - Should EXPOSE port 5000
    - The CMD statement should be at the end and it should call `python app.py`

5. **Update the `docker-compose.yml`:**

    - Add a new service for Flask.
    - Configure the Flask service to:
        - Build the image from the project directory. Here's a sample snippet to help with this, this should go in place of the `image: <image>:<tag>` line we usually use:
            ```bash
            # EXAMPLE
            my-new-service:
              build:
                context: . 
                # The location to look for the Dockerfile, 
                # can only be either current directory or
                # descendant directory
                
                dockerfile: Dockerfile 
                # *optional: The name of the file containing 
                # Dockerfile instructions. Default: `Dockerfile`
            ```
            - **HINT**: You may have to change your `context: .`
        - Map port `5000` inside the container to port `5000` on the host.
        - Use `depends_on` to ensure the ***database*** and the ***nginx web*** services starts before the Flask app.
        - Update the `db` service to expose its port for connections. 
            - **HINT**: Remember the MySQL runs on port 3306

6. **Build and Run:**

    Build and run the services:

    ```bash
    docker compose up --build
    ```

7. **Verify:**
    - Visit `http://localhost:5000/` to see the Flask app.
    - Visit `http://localhost:5000/data` to confirm connection to the database.


---

### **Expected Output:**
- NGINX serves a custom HTML page.
- Flask app runs at port 5000 and interacts with the MySQL database.

