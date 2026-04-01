importScripts('https://www.gstatic.com/firebasejs/10.13.0/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/10.13.0/firebase-messaging.js');

const firebaseConfig = {
  apiKey: "AIzaSyBUef15crXKCD2AhIhSceQajbFBkEA2urg",
  authDomain: "push-notification-a806b.firebaseapp.com",
  projectId: "push-notification-a806b",
  storageBucket: "push-notification-a806b.appspot.com",
  messagingSenderId: "329285620602",
  appId: "1:329285620602:web:60789ccd0416a3aea73cc3",
  measurementId: "G-CQN7258F0V"
};

firebase.initializeApp(firebaseConfig);

const messaging = firebase.messaging();

messaging.onBackgroundMessage(function(payload) {
  console.log('[firebase-messaging-sw.js] Received background message ', payload);
  const notificationTitle = payload.notification.title;
  const notificationOptions = {
    body: payload.notification.body,
    icon: '/firebase-logo.png'  // Ensure this icon is correctly referenced
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});