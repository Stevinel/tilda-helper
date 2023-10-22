# Tilda-helper 🚀

**Tilda-helper** is an automation tool designed to streamline the sales process for lingerie patterns from a Tilda website. Traditionally, the Tilda platform has limitations, and Tilda-helper offers an automated way to send PDF files with patterns directly to customers, saving the owner the hassle of manual operations.

## 🎯 Project Overview

The core idea behind Tilda-helper is to provide an automated method for distributing lingerie patterns. Since Tilda doesn't inherently support sending pattern files directly, users would have to create a separate page for each pattern. This isn't feasible, especially with a large inventory.

Here's how Tilda-helper operates:
- The project receives order details for patterns from the Tilda site via webhooks.
- It then serializes this data, conducts various validations, and stores the order with all pertinent details about the client, their order, and the products within the order.
- Following this, Tilda-helper sends all PDF files with patterns from the order to the client's specified email address.
- In parallel, the project notifies the site owner's Telegram group about the receipt and dispatch of the order. If there's an error at any stage, the group is promptly informed.

Previously, the owner had to manually execute this entire workflow, a tedious process he followed for nearly two years. This involved checking the order table multiple times a day, marking new orders, and manually dispatching patterns to each client. With Tilda-helper, this entire process is automated, saving time and effort.

## 🌟 Features

1. **Webhook Data Processing**: Receives orders via a webhook from Tilda and processes them.
2. **Telegram Bot Integration**: Accepts data via a Telegram bot and sends orders to email.
3. **Email Notifications**: Automatically sends purchased patterns to clients.
4. **Client Data Management**: Stores client data with diverse filtering options.
5. **Telegram and Sentry Error Reporting**: Notifies in Telegram about successful processes or errors and reports issues in Sentry.
6. **Admin Panel Security**: Limits admin panel access after three failed attempts.
7. **Database Management**: Performs weekly database dumps.
8. **Product Management**: Stores product information and offers multiple sorting options.
9. **Order Management**: Keeps detailed order records with sorting capabilities.
10. **Docker Container Monitoring**: Updates on Docker container statuses via Telegram.
11. **Newsletter Feature**: Allows broadcasting news to all clients, useful for announcing new products.

## 🛠️ Tech Stack

- Django
- Python
- FastAPI
- Telebot
- Docker-compose
- Nginx
- Celery
- Sentry
- Postgres

## 🔧 Installation

1. Clone the repository:
   ```bash
   git clone <repository-link>
   ```


2. Set enviroments:
    ```DB_PASS='db pass'
    DB_USER='db user'
    DB_NAME='db name'
    DB_PORT='db port'
    DB_HOST='db host'
    
    SECRET_KEY='django secret key'
    CSRF_TRUSTED_DOMAINS='http://domain'
    ALLOWED_HOSTS='127.0.0.1, domain,'
    DEBUG='True' # or 'False' for production
    DOMAIN='your domain'
    
    TELEGRAM_TOKEN='your_telegram_token'
    TARGET_CHAT_ID='your_chat_id'
    
    API_NAME='your api name from tilda'
    API_KEY='your api key from tilda'
    
    ADMIN_URL='admin/' # or custom admin URL
    
    EMAIL=your email
    EMAIL_TOKEN=email token
    
    CELERY_BROKER=redis://redis:6379/0
    DNS='your dns'
    SENTRY_DNS='your sentry link'
    
    ALLOWED_CHATS='your_tg_ids'
   ```