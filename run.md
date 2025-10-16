
```powershell
cd "c:\Users\imadb\OneDrive\Bureau\Feederated Learning"
.\RUN.bat
```






###  `del /s /q *.pyc >nul 2>&1`

 Deletes all Python cache files (`.pyc`) **recursively** in the current folder and subfolders.

* `/s` → include subfolders
* `/q` → quiet mode (no confirmation)
* `>nul 2>&1` → hide any output or errors.

💡 Cleans the project before running to avoid cached code issues.

---

###  `for /d /r %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul`

 Searches **recursively** for folders named `__pycache__` and deletes them too (same idea: clean-up Python cache folders).
This ensures you’re running clean Python code.

---

###  `start /min "Global Server" cmd /c "cd /d %CD%\orchestration && python start_global_server.py"`

 Starts a new **minimized terminal window** (so it doesn’t block this script).

* `"Global Server"` → the title of that window.
* `cd /d %CD%\orchestration` → go to the orchestration folder.
* `python start_global_server.py` → runs the Python script that starts the **global server** (probably your central API or orchestrator).
* `/min` → opens minimized.
* `cmd /c` → runs the command and closes that window when done.

---

###  `timeout /t 3 /nobreak >nul`

 Waits **3 seconds** (to let the Global Server start up) before starting the next service.
`/nobreak` means you can’t skip it by pressing a key.

---

###  `start /min "Kafka Producer" cmd /c "cd /d %CD%\orchestration && python start_streaming.py"`

 Starts another window for the Kafka producer — the script that simulates or sends streaming data to Kafka topics.

---

###  `timeout /t 2 /nobreak >nul`

 Waits 2 seconds before starting the next process.

---

###  `start /min "Flink Job" cmd /c "cd /d %CD%\orchestration && python start_flink.py"`

 Starts the Flink streaming job — this one will probably consume messages from Kafka and process them.

---

###  `timeout /t 2 /nobreak >nul`

 Again, wait 2 seconds.

---

###  `start /min "Spark Jobs" cmd /c "cd /d %CD%\orchestration && python start_spark_jobs.py"`

 Finally starts the Spark job — probably for batch or analytical processing.

---

 **In summary**, this script:

1. Cleans all Python caches.
2. Starts your entire data pipeline **in sequence**:

   * Global server
   * Kafka producer
   * Flink job
   * Spark job
3. Runs each in a separate minimized command window.
4. Waits a few seconds between each step to let them initialize properly.

---

If you run this on Windows (by double-clicking or from CMD), it launches your whole architecture automatically.
Would you like me to rewrite it for **Linux/macOS (bash)** version too?
