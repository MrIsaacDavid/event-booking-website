from website import create_app

#imports every in the website and used to run a project and start a web server.
app=create_app()
 

 #helps to keep website running as it updates and comes to hault when it encounters error 
 # it runs the webserver and ensures that the app only runs if this script is executed directly, not imported as a module.
if __name__ == '__main__': 
    app.run(debug=True) 


