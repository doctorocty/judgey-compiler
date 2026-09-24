Judgey Compiler is a web based code compiler. Except, it doesn't exactly like you.

Made for a Halloween hackathon, Judgey Compiler starts off looking pretty normal. You write your code, run it, and get your output. But every mistake you make makes it worse. More errors mean creepier pictures, darker sounds, and a progressively more cursed experience.

So yeah... maybe don't make mistakes.

What it does

Judgey Compiler lets you write and run Python, JavaScript, C, C++, and Java. It uses Flask for the backend and CodeMirror for the editor. Python errors are checked with Pyflakes, JavaScript with ESLint, and C, C++, and Java are compiled using their respective compilers. The backend counts your errors and sends the result to the frontend, which changes the horror level based on how badly you messed up. There are 5 horror levels, each with different pictures and sounds.

Installation

You'll need Python, Node.js, npm, GCC, G++, Java JDK, and Git.

git clone https://github.com/doctorocty/judgey-compiler.git
cd judgey-compiler
python -m venv venv

On Windows:
venv\Scripts\activate

On macOS/Linux:
source venv/bin/activate
Install the dependencies:
pip install -r requirements.txt
npm install

Make sure everything is installed:

python --version
node --version
gcc --version
g++ --version
javac --version

Then start the compiler:
python app.py
Open the local URL shown in your terminal.
Docker
You can also run it with Docker:
docker build -t judgey-compiler .
docker run -p 10000:10000 judgey-compiler
Then open http://localhost:10000.

A tiny warning-

Judgey Compiler actually runs the code you give it. There are timeouts and resource limits, but the current sandbox isn't meant to be a perfect security system. If you're deploying it publicly, proper isolation should be added before letting random people run code on your server.

The idea:

I wanted to make a compiler that doesn't just tell you that your code is wrong. I wanted it to make you feel like it's getting angry at you. At first, everything is fine. Then you make a mistake. Then another. the music changes. The screen changes. And eventually, the compiler starts looking like it really doesn't want you there.

Happy Halloween :3
