# Getting started with Streamlit

30 minutes. By the end, you will have Streamlit installed, a tiny working app running in your
browser, and a project ready for the challenge. This does not build any of the challenge
features. It only gets you to the point where you can start.

Official docs for everything here: https://docs.streamlit.io/get-started

---

## Step 1: a separate project, a separate environment (5 minutes)

Do this before installing anything.

Your FastAPI project needs `starlette` below version 0.42. Streamlit needs `starlette` at
0.46 or above. These two requirements cannot both be satisfied in the same environment.
Installing Streamlit into your existing project's virtual environment will break your API.

Create a new folder, next to your API project, not inside it.

```bash
cd ..
mkdir firm-intelligence-ui
cd firm-intelligence-ui
```

Create a new virtual environment inside it.

```bash
python -m venv .venv
```

Activate it.

```bash
.venv\Scripts\activate
```

You should see `(.venv)` at the start of your terminal prompt once this has worked.

---

## Step 2: install Streamlit (5 minutes)

Official install guide: https://docs.streamlit.io/get-started/installation

```bash
pip install streamlit httpx
```

`streamlit` is the framework itself. `httpx` is what will let your app talk to your API,
same library you have already used this week.

Confirm the install worked, using Streamlit's own built in demo app:

```bash
streamlit hello
```

This should open a browser tab on its own, showing Streamlit's example app. If it opens,
Streamlit is correctly installed. Close that tab, this demo is not your project, it is only
a check that the install worked. Stop it in your terminal with Ctrl+C.

---

## Step 3: your first, real, empty app (10 minutes)

Official concepts guide: https://docs.streamlit.io/get-started/fundamentals/main-concepts

In your `firm-intelligence-ui` folder, create a file called `app.py`.

```python
import streamlit as st

st.title("Firm Intelligence")
st.write("If you can see this, the setup worked.")
```

Run it.

```bash
streamlit run app.py
```

A browser tab should open showing your title and your sentence. Leave this terminal running,
same as you leave `uvicorn` running for your API. Streamlit watches the file and reloads
automatically every time you save.

---

## Step 4: one input, one button, proof it is interactive (10 minutes)

Add this below what you already have in `app.py`.

```python
name = st.text_input("Type something")

if st.button("Click me"):
    st.write("You typed:", name)
```

Save. Go back to the browser tab, it should have already reloaded. Type something in the box,
click the button, and confirm your text appears below it.

This is the whole interaction pattern the challenge is built on. A widget collects input, a
button triggers an action, `st.write` (or something like it) displays a result. Everything
in the challenge is this same pattern, aimed at your real API instead of just echoing text
back.

---

## Before you move on to the challenge

Confirm all of the following are true.

- [ ] `streamlit run app.py` opens a working page in your browser
- [ ] Typing in the box and clicking the button shows your text back
- [ ] This is running in its own `firm-intelligence-ui` folder, its own virtual environment
- [ ] Your actual FastAPI project is untouched, and still runs fine on its own

If all four are true, you are ready to start the challenge. If your API is not currently
running, start it now, in its own terminal, before you begin.

## Where to go if you get stuck

Official docs, in the order they will actually help you:

- Installation problems: https://docs.streamlit.io/get-started/installation
- What a specific function does: https://docs.streamlit.io/develop/api-reference
- General concepts, how Streamlit thinks about apps: https://docs.streamlit.io/get-started/fundamentals/main-concepts
- If I am out of the room, drop me a message, if not, just shout!!
