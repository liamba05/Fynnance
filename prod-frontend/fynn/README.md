# Fynn Financial Assistant

Fynn is a financial assistant application that helps users with budgeting, investments, and financial planning.

## Quick Start Guide

Follow these steps to run the application locally:

### 1. Start the Frontend

```bash
# Navigate to the frontend directory
cd /Users/liambouayad/Documents/GitHub/Fynn/prod-frontend/fynn

# Install dependencies (first time only)
npm install

# Start the development server
npm run dev
```

The frontend will be available at: `http://localhost:5173`

### 2. Start the Backend (Python API)

```bash
# Navigate to the backend directory
cd /Users/liambouayad/Documents/GitHub/Fynn/backend

# Create and activate virtual environment (first time only)
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

# Install dependencies (first time only)
pip install -r requirements.txt

# Start the backend server
python UserDataCollection/run_api.py
```

The backend API will be available at: `http://localhost:5002`

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type aware lint rules:

- Configure the top-level `parserOptions` property like this:

```js
export default tseslint.config({
  languageOptions: {
    // other options...
    parserOptions: {
      project: ['./tsconfig.node.json', './tsconfig.app.json'],
      tsconfigRootDir: import.meta.dirname,
    },
  },
})
```

- Replace `tseslint.configs.recommended` to `tseslint.configs.recommendedTypeChecked` or `tseslint.configs.strictTypeChecked`
- Optionally add `...tseslint.configs.stylisticTypeChecked`
- Install [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) and update the config:

```js
// eslint.config.js
import react from 'eslint-plugin-react'

export default tseslint.config({
  // Set the react version
  settings: { react: { version: '18.3' } },
  plugins: {
    // Add the react plugin
    react,
  },
  rules: {
    // other rules...
    // Enable its recommended rules
    ...react.configs.recommended.rules,
    ...react.configs['jsx-runtime'].rules,
  },
})
```
