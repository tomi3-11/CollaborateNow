
# CollaborateNow

[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.x-green.svg)](https://www.djangoproject.com/)
[![Channels](https://img.shields.io/badge/Channels-4.x-orange.svg)](https://channels.readthedocs.io/en/stable/)
[![Redis](https://img.shields.io/badge/Redis-Connected-red.svg)](https://redis.io/)
[![Maintenance](https://img.shields.io/badge/Maintained-Yes-brightgreen.svg)](https://github.com/tomi3-11/https://github.com/tomi3-11/CollaborateNow.git/graphs/commit-activity)
[![Contributors](https://img.shields.io/github/contributors/your-github-username/your-repo-name)](https://github.com/tomi3-11/https://github.com/tomi3-11/CollaborateNow.git/graphs/contributors)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-v2.1%20adopted-ff69b4.svg)](CODE_OF_CONDUCT.md)

**A powerful and intuitive web-based platform designed to enhance team collaboration and project management.**

## Overview

The Collaborative Team Platform is engineered to streamline teamwork by providing a suite of essential tools in one centralized location. From managing projects and tasks to fostering real-time communication and sharing resources, this platform aims to boost productivity and improve team cohesion.

**Key Features:**

* **Project Management:** Organize and track multiple projects with clear objectives, rules, goals, and deadlines.
* **Team Collaboration:** Facilitate seamless interaction among team members within dedicated project spaces.
* **Real-time Chat:** Engage in instant messaging with project members to discuss ideas and updates.
* **Shared Whiteboard:** Brainstorm and visualize concepts collaboratively in real-time.
* **Task Management:** Create, assign, track, and manage tasks with status updates and due dates.
* **File Sharing:** Easily upload and share relevant documents and resources within projects.
* **Activity Feed:** Stay informed with a real-time stream of all project activities, ensuring everyone is on the same page.
* **User Profiles:** Manage individual profiles with optional avatars and skill listings.
* **GitHub Integration:** Link project repositories to display relevant information (e.g., repository URL).
* **Skill-Based Collaboration:** Define required skills for projects to help find suitable collaborators.
* **Notifications:** Stay updated with important events and activities within your projects.

## Table of Contents

* [Overview](#overview)
* [Key Features](#key-features)
* [Getting Started](#getting-started)
    * [Prerequisites](#prerequisites)
    * [Installation](#installation)
    * [Configuration](#configuration)
    * [Running the Development Server](#running-the-development-server)
    * [Running the Channels Development Server](#running-the-channels-development-server)
* [Project Structure](#project-structure)
* [Contributing](#contributing)
* [Code of Conduct](#code-of-conduct)
* [License](#license)
* [Support](#support)
* [Acknowledgments](#acknowledgments)

## Getting Started

Follow these instructions to get a local copy of the project up and running for development and testing purposes.

### Prerequisites

Ensure you have the following installed on your system:

* **Python:** Version 3.9 or higher ([https://www.python.org/downloads/](https://www.python.org/downloads/))
* **pip:** Python package installer (usually included with Python)
* **Django:** Version 4.x ([https://docs.djangoproject.com/en/stable/intro/install/](https://docs.djangoproject.com/en/stable/intro/install/))
* **Channels:** Version 4.x ([https://channels.readthedocs.io/en/stable/installation.html](https://channels.readthedocs.io/en/stable/installation.html))
* **Redis:** For the real-time features powered by Channels ([https://redis.io/download/](https://redis.io/download/))
* **A Database:** PostgreSQL is recommended for production, but SQLite can be used for development. Ensure you have the necessary drivers installed if using PostgreSQL or MySQL.
* **Git:** For version control ([https://git-scm.com/downloads](https://git-scm.com/downloads))

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/tomi3-11/CollaborateNow.git
    cd CollaborateNow
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On macOS/Linux
    venv\Scripts\activate  # On Windows
    ```

3.  **Install the project dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Configuration

1.  **Database Setup:**
    * Configure your database settings in the `CollaborateNow/settings.py` file. Update the `DATABASES` dictionary with your database credentials.
    * Run database migrations to create the necessary tables:
        ```bash
        python manage.py makemigrations accounts
        python manage.py migrate
        ```
    * Create a superuser to access the Django admin panel:
        ```bash
        python manage.py createsuperuser
        ```

2.  **Redis Configuration:**
    * Ensure your Redis server is running.
    * Verify the Channels layer configuration in `CollaborateNow/settings.py` under `CHANNEL_LAYERS`. The default configuration usually works for local development.

3.  **Environment Variables (Optional but Recommended):**
    * For sensitive information like database credentials and secret keys, consider using environment variables. You can use a `.env` file (add it to `.gitignore`) and a library like `python-dotenv`.

### Running the Development Server

To run the standard Django development server:

```bash
python manage.py runserver