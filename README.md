
---

# 🍽️ Family Restaurant — Floating Chat Widget

An **AI-powered customer support chat widget** designed for **family restaurants** to automatically answer common customer questions like hours, menu items, directions, reservations, and more — all in real time.

Originally built for [Dlanos Family Restaurant](https://www.dlanosrestaurant.ca), this widget is **fully customizable** and can be easily adapted for **any restaurant** or **local business** looking to enhance their customer experience with intelligent automation.

---

## Features

*  **Floating Chat Widget** — A sleek, minimal, and mobile-friendly chat button that stays on every page.
*  **AI Responses (GPT-4o-mini)** — Provides accurate, conversational answers about your restaurant.
*  **FastAPI Backend** — Lightweight, efficient API server for chat and context handling.
* **Custom Knowledge Base** — Feed the AI with your restaurant’s menu, location, or FAQs.
* **Easy Integration** — Just embed one line of JavaScript into your existing website.
* **Multi-Restaurant Ready** — Works for any family restaurant — just change the config.
* **Privacy-Friendly** — No customer data is stored unless you explicitly enable logging.

---

## Tech Stack

| Component  | Technology                                                 |
| ---------- | ---------------------------------------------------------- |
| Frontend   | HTML, CSS, JavaScript (Vanilla / Widget)                   |
| Backend    | FastAPI                                                    |
| AI Engine  | OpenAI GPT-4o-mini                                         |
| Deployment | Any platform supporting Python (Render, Vercel, AWS, etc.) |

---

## ⚙️ How It Works

1. **Frontend Widget**

   * A floating chat icon loads on every page of your site.
   * When clicked, it opens a small chat window.

2. **Backend (FastAPI)**

   * The user’s question is sent to the FastAPI server.
   * The server queries OpenAI’s GPT-4o-mini model with your custom restaurant context.
   * The response is sent back instantly to display in the chat window.

3. **Customization**

   * Add your own FAQs, business hours, or menu details in a simple JSON or YAML file.
   * The AI uses that data to tailor its answers to your restaurant.

---

## 🧩 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/harmansingh2005/family-restaurant-chat-widget.git
cd family-restaurant-chat-widget
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Add Your OpenAI API Key

Create a `.env` file in the root directory:

```
OPENAI_API_KEY=your_openai_api_key_here
```

### 5. Run the FastAPI Server

```bash
uvicorn main:app --reload
```

### 6. Embed the Widget in Your Website

Add this inside your website’s `<body>` tag:

```html
<script src="https://your-server.com/widget.js"></script>
```

That’s it! The floating chat icon will appear automatically on your site.

---

## 🧰 Configuration

You can edit the `config.yaml` or `faq.json` file to include:

```yaml
restaurant_name: "Dlanos Family Restaurant"
hours: "Mon–Sat: 10AM–10PM, Sun: Closed"
address: "123 Main St, Toronto, ON"
menu_url: "https://www.dlanosrestaurant.ca/menu"
phone: "+1 (555) 123-4567"
faq:
  - "Do you offer vegetarian options?"
  - "Can I make a reservation online?"
```

---

##  Example Use Cases

* **Family Restaurants** — Instant answers to menu, pricing, and hours.
* **Cafés & Bakeries** — Customers can ask about daily specials or ingredients.
* **Hotels or Resorts** — Integrate with dining pages for guest support.
* **Food Trucks** — Let customers know today’s location and operating hours.

---

## Deployment

This app can be easily deployed on:

* **Render / Railway / Vercel** — One-click FastAPI deployment.
* **AWS Lambda or EC2** — For production scalability.
* **Docker** — Use the provided `Dockerfile` for containerized deployment.

---

##  Future Enhancements

* 🔊 Voice chat mode
* 📅 Reservation system integration
* 🧾 Dynamic menu parsing from website
* 🌐 Multi-language support
* 📊 Analytics dashboard for chat insights

---

##  Contributing

Contributions are welcome!
If you’d like to add new features or fix bugs:

1. Fork the repo
2. Create a feature branch
3. Submit a pull request

---

##  License

This project is licensed under the **MIT License** — free for personal and commercial use.

---
