import React from 'react';
import ReactDOM from 'react-dom';
import {App} from './App';
import {Provider} from "react-redux";
import {store} from "./store";
import {ErrorBoundary} from "./Feedback";


import * as serviceWorkerRegistration from './serviceWorkerRegistration';


ReactDOM.render(
  <Provider store={store}>
    <ErrorBoundary>
      <App/>
    </ErrorBoundary>
  </Provider>,
  document.getElementById("root")
);

// Fork local: NAO registrar service worker — ele grudava builds antigos no navegador.
// unregister() remove qualquer SW ja instalado em quem abriu uma versao anterior.
serviceWorkerRegistration.unregister();
