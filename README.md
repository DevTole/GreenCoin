# 🌿 GreenCoin - Eco-Friendly Digital Wallet & Marketplace

<div align="center">
  <img src="https://i.postimg.cc/c4XP7f51/1776282289238.png" alt="GreenCoin Logo" width="120" height="120" style="border-radius: 20px;">
  
  **Your Gateway to Sustainable Digital Transactions**
  
  [![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
  [![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
  [![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-blue.svg)](https://www.postgresql.org/)
  [![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
</div>

---

## 📖 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Screenshots](#screenshots)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [Contributing](#contributing)
- [License](#license)

---

## 🌍 Overview

GreenCoin is a revolutionary eco-friendly digital wallet and marketplace platform that rewards users for sustainable practices. Users can earn, trade, and spend GreenCoins on recycled materials and eco-friendly products. The platform features a beautiful, responsive design with dark/light mode support.

<div align="center">
  <img src="https://via.placeholder.com/800x400/2ecc71/ffffff?text=GreenCoin+Dashboard" alt="Dashboard Preview" style="border-radius: 20px; max-width: 100%;">
</div>

---

## ✨ Features

### 🔐 **Secure Authentication**
- Argon2 password hashing for maximum security
- Session-based authentication with Flask-Login
- User registration with language preferences

<div align="center">
  <table>
    <tr>
      <td><img src="https://via.placeholder.com/400x300/ffffff/2ecc71?text=Login+Page" alt="Login" style="border-radius: 10px;"></td>
      <td><img src="https://via.placeholder.com/400x300/ffffff/2ecc71?text=Signup+Page" alt="Signup" style="border-radius: 10px;"></td>
    </tr>
  </table>
</div>

### 💰 **Digital Wallet**
- Real-time balance tracking
- Privacy-focused blur toggle for sensitive information
- Unique GreenCoin wallet ID generation
- QR code generation and scanning capabilities

<div align="center">
  <img src="https://via.placeholder.com/400x300/1a1a2e/2ecc71?text=Wallet+Interface" alt="Wallet Interface" style="border-radius: 10px;">
</div>

### 🛍️ **Eco Marketplace**
- Browse and purchase eco-friendly products
- Quantity controls for precise ordering
- Seamless add-to-cart functionality
- Product image support with fallback

<div align="center">
  <img src="https://via.placeholder.com/400x300/242440/2ecc71?text=Marketplace+View" alt="Marketplace" style="border-radius: 10px;">
</div>

### 🛒 **Shopping Cart**
- Review items before checkout
- Individual item management (buy now/delete)
- Balance verification for purchases
- Total cost calculation

### 💸 **Peer-to-Peer Transactions**
- Send GreenCoins via QR code scanning
- Receive payments with shareable QR codes
- Transaction confirmation modals
- Real-time payment processing

<div align="center">
  <table>
    <tr>
      <td><img src="https://via.placeholder.com/400x300/1a1a2e/2ecc71?text=Send+Payment" alt="Send" style="border-radius: 10px;"></td>
      <td><img src="https://via.placeholder.com/400x300/1a1a2e/2ecc71?text=Receive+QR" alt="Receive" style="border-radius: 10px;"></td>
    </tr>
  </table>
</div>

### 🎨 **UI/UX Excellence**
- **Dark/Light Mode**: Seamless theme switching
- **Floating Navigation**: Detached, modern design
- **Liquid Animation**: Smooth page transitions with pour effect
- **Skeleton Loading**: Elegant loading states
- **Frosted Glass Effects**: Modern blur effects for privacy
- **Responsive Design**: Mobile-first approach

<div align="center">
  <img src="https://via.placeholder.com/800x300/0f0f1a/2ecc71?text=Dark+Mode+Interface" alt="Dark Mode" style="border-radius: 10px;">
</div>

---

## 🛠️ Tech Stack

<div align="center">
  <table>
    <tr>
      <td align="center"><strong>Backend</strong></td>
      <td align="center"><strong>Frontend</strong></td>
      <td align="center"><strong>Database</strong></td>
      <td align="center"><strong>Security</strong></td>
    </tr>
    <tr>
      <td>
        • Python 3.8+<br>
        • Flask Framework<br>
        • SQLAlchemy<br>
        • Flask-Login
      </td>
      <td>
        • HTML5/CSS3<br>
        • Vanilla JavaScript<br>
        • Ionicons<br>
        • HTML5 QR Code
      </td>
      <td>
        • PostgreSQL<br>
        • NeonDB (Cloud)
      </td>
      <td>
        • Argon2 Hashing<br>
        • Session Management<br>
        • HTTPS Ready
      </td>
    </tr>
  </table>
</div>

---

## 📦 Installation

### Prerequisites

```bash
# System Requirements
- Python 3.8 or higher
- PostgreSQL 14 or higher
- Git
- pip (Python package manager)
