
*****app.py*****

This is your main entry point — it:
    Initializes the Dash app
    Sets up page routing (/run-individual-model, /run-cluster-model, etc.)
    Registers callbacks from submodules (your pages)
    Defines a small loader animation callback


*****pages/choose_approach.py

✅ What this file does

    choose_approach.py is purely a navigation/landing page.

    It shows two buttons → “Individual Tariff” and “Cluster Tariff.”

    Based on which is clicked, it redirects to either:

    /run-individual-model

    /run-cluster-model

There’s no data reading, file upload, or input handling in this file — it’s just the UI for approach selection.

*****pages/run_individual_model.py

