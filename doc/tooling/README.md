# Tools used in the project
The following lists the tools and frameworks, that are used in the project. 
- [Docker](https://docs.docker.com/get-started/overview/)    
   Docker is an open platform for developing, shipping, and running applications. Docker enables you to separate your applications from your infrastructure so you can deliver software quickly. With Docker, you can manage your infrastructure in the same ways you manage your applications. By taking advantage of Docker's methodologies for shipping, testing, and deploying code, you can significantly reduce the delay between writing code and running it in production.
- [Kubernetes](https://kubernetes.io/docs/concepts/overview/)

    Kubernetes is a portable, extensible, open source platform for managing containerized workloads and services that facilitates both declarative configuration and automation.

    It has a large, rapidly growing ecosystem.

    Kubernetes services, support, and tools are widely available.

    Kubernetes provides you with a framework to run distributed systems resiliently.

    It takes care of scaling and failover for your application, provides deployment patterns, and more.
- [FastAPI](https://fastapi.tiangolo.com/tutorial/)
-  FastAPI is a modern, fast (high-performance), web framework for building APIs with Python based on standard Python type hints. 
- Fast: Very high performance, on par with NodeJS and Go (thanks to Starlette and Pydantic). 
- Fast to code: Increase the speed to develop features by about 200% to 300%. 
- Fewer bugs: Reduce about 40% of human (developer) induced errors. 
- Standards-based: Based on (and fully compatible with) the open standards for APIs: OpenAPI (previously known as Swagger) and JSON Schema.
- [SQLAlchemy](https://docs.sqlalchemy.org/en/20/orm/quickstart.html)
- SQLAlchemy is the Python SQL toolkit and Object Relational Mapper that gives application developers the full power and flexibility of SQL. 
- It provides a full suite of well known enterprise-level persistence patterns, designed for efficient and high-performing database access, adapted into a simple and Pythonic domain language. 
- SQLAlchemy is an open-source SQL toolkit and Object-Relational Mapping (ORM) system for Python. 
- It provides developers with the flexibility of using SQL databases in a Pythonic way. 
- This means developers can work with Python objects and do not need to write separate SQL queries.
- [FastAPI with SQLAlchemy](https://fastapi.tiangolo.com/tutorial/sql-databases/)
- [Alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- Alembic is a lightweight database migration tool for usage with the SQLAlchemy Database Toolkit for Python. 
- Alembic is a database migrations tool written by the author of SQLAlchemy. 
- A migrations tool offers the following functionality: can emit ALTER statements to a database in order to change the structure of tables and other constructs. 
- It provides a system whereby “migration scripts” may be constructed; each script indicates a particular series of steps that can upgrade a target database to a new version, and optionally a series of steps that can downgrade similarly, doing the same steps in reverse.

Alembic allows the scripts to execute in some sequential manner.
- [Swagger UI](https://swagger.io/tools/swagger-ui/)
- Swagger UI allows anyone — be it your development team or your end consumers — to visualize and interact with the API’s resources without having any of the implementation logic in place. 
- It’s automatically generated from your OpenAPI (formerly known as Swagger) Specification, with the visual documentation making it easy for back end implementation and client side consumption. 
- Swagger UI is a collection of HTML, JavaScript, and CSS assets that dynamically generate beautiful documentation from a Swagger-compliant API. 
- Swagger UI is a dependency-free collection of HTML, JavaScript, and CSS assets that dynamically generate beautiful documentation from a Swagger-compliant API.
- [Ruff](https://github.com/astral-sh/ruff)

# GitLab CI/CD

The following is a collection of short hints on how to do the most essential things in a GitLab CI/CD pipeline:

- How to delay a job until another job is done: 
    Use `needs` to define a dependency job. Alternatively, define a `stage` - jobs in a later stage run only after all the jobs in the earlier stage are done.
- How to change the image used in a task: 
    Change the `image` to `<imagename>:<tag>`. Using `latest` as a tag is possible, but hurts reproduceability.
- How do you start a task manually:
    Go to the pipeline page, find the task in the "Stage" tab and click the "Run" button.
- The Script part of the config file - what is it good for?
    It is a list of commands that will be executed - could be used to output useful info (for example, Kubernetes Dashboard link, as showcased in this repo in print_readme job).
- If I want a task to run for every branch I put it into the stage ??check:
    commit
- If I want a task to run for every merge request I put it into the stage ??:
    acceptance
- If I want a task to run for every commit to the main branch I put it into the stage ??:
    release
# Ruff

- What is the purpose of ruff?
    Ruff is a linter and a static code analysis tool, performing linting and code formatting. In our project, we run it via the ruff_checking job, linting everything in app/ and tests/.
- What types of problems does it detect?
    It ensures that code follows conventions, checks for potential errors (without actually running the code), and even checks for potential security vulnerabilities.
- Why should you use a tool like ruff in a serious project?
    It helps to ensure code quality, simplifies code review and establishes a formatting standard - all automatically.
## Run ruff on your local Computer

  It is very annoying (and takes a lot of time) to wait for the pipeline to check the syntax 
  of your code. To speed it up, you may run it locally like this:

### Configure PyCharm (only once)
- find out the name of your docker container containing ruff. Open the tab *services* in PyCharm and look at the container in the service called *web*. The the name should contain the string *1337_pizza_web_dev*.  
- select _Settings->Tools->External Tools_ 
- select the +-sign (new Tool)
- enter Name: *ruff-docker*
- enter Program: *docker*
- enter Arguments (replace the first parameter with the name of your container): 
    *exec -i NAMEOFYOURCONTAINER ruff check --exclude /opt/project/app/api/database/migrations/ /opt/project/app/api/ /opt/project/tests/*
- enter Working Directory: *\$ProjectFileDir\$*

If you like it convenient: Add a button for ruff to your toolbar!
- right click into the taskbar (e.g. on one of the git icons) and select *Customize ToolBar*
- select the +-sign and Add Action
- select External Tools->ruff-docker

### Run ruff on your project
  - Remember! You will always need to run the docker container called *1337_pizza_web_dev* of your project, to do this! 
    So start the docker container(s) locally by running your project
  - Now you may run ruff 
      - by clicking on the new icon in your toolbar or 
      - by selecting from the menu: Tools->External Tools->ruff-docker 

# GrayLog

- What is the purpose of GrayLog?

- What logging levels are available?

- What is the default logging level?

- Give 3-4 examples for logging commands in Python:
  ```python

  ```

# SonarQube

- What is the purpose of SonarQube?

- What is the purpose of the quality rules of SonarQube?

- What is the purpose of the quality gates of SonarQube?


## Run SonarLint on your local Computer

It is very annoying (and takes a lot of time) to wait for the pipeline to run SonarQube. 
To speed it up, you may first run the linting part of SonarQube (SonarLint) locally like this:

### Configure PyCharm for SonarLint (only once)

- Open *Settings->Plugins*
- Choose *MarketPlace*
- Search for *SonarLint* and install the PlugIn

### Run SonarLint

- In the project view (usually to the left) you can run the SonarLint analysis by a right click on a file or a folder. 
  You will find the entry at the very bottom of the menu.
- To run it on all source code of your project select the folder called *app*

# VPN

The servers providing Graylog, SonarQube and your APIs are hidden behind the firewall of Hochschule Darmstadt.
From outside the university it can only be accessed when using a VPN.
https://its.h-da.io/stvpn-docs/de/ 