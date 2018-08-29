const electron = require('electron')
const {ipcMain} = require('electron');

// Module to control application life.
const app = electron.app
// Module to create native browser window.
const BrowserWindow = electron.BrowserWindow

const path = require('path');
const url = require('url');

// Keep a global reference of the window object, if you don't, the window will
// be closed automatically when the JavaScript object is garbage collected.
let mainWindow

class Main {
	constructor() {
		this.mainWindow = null;
		this.addListeners();
	}

	createWindow() {
		// Create the browser window.
		this.mainWindow = new BrowserWindow({
			width: 1920, 
			height: 1080,
			resizable: true
		});

		
		// and load the index.html of the app.
		this.mainWindow.loadURL(url.format({
			pathname: path.join(__dirname, 'smash.html'),
			protocol: 'file:',
			slashes: true
		}));

		// Open the DevTools.
		//this.mainWindow.webContents.openDevTools()
		//// Emitted when the window is closed.
		this.mainWindow.on('closed', function () {
			// Dereference the window object, usually you would store windows
			// in an array if your app supports multi windows, this is the time
			// when you should delete the corresponding element.
			this.mainWindow = null;
		});
	}

	addListeners() {
		// This method will be called when Electron has finished
		// initialization and is ready to create browser windows.
		// Some APIs can only be used after this event occurs.
		app.on('ready', this.createWindow);

		// Quit when all windows are closed.
		app.on('window-all-closed', function () {
			// On OS X it is common for applications and their menu bar
			// to stay active until the user quits explicitly with Cmd + Q
			if (process.platform !== 'darwin') {
				app.quit();
			}
		});

		app.on('activate', function () {
			// On OS X it's common to re-create a window in the app when the
			// dock icon is clicked and there are no other windows open.
			if (this.mainWindow === null) {
				this.createWindow();
			}
		});
	}
}

// Attach listener in the main process with the given ID
ipcMain.on('request-mainprocess-action', (event, arg) => {
    // Displays the object sent from the renderer process:
    //{
    //    message: "Hi",
    //    someData: "Let's go"
    //}
    console.log(
        arg
    );
});

new Main();
