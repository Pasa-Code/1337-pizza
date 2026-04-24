import { h, FunctionComponent } from 'preact';
import { OrderListComponent } from './components/OrderListComponent';
import { BeveragesListComponent } from './components/BeveragesListComponent';
import { DoughListComponent } from './components/DoughListComponent';
import { PizzaTypesListComponent } from './components/PizzaTypesListComponent';
import { ToppingsListComponent } from './components/ToppingsListComponent';

import { useContext, useEffect } from 'preact/hooks';
import { ACTION_CHECK_DEFAULT_USER, 
  ACTION_DELETE_ALL, 
  ACTION_FETCH_ALL_AWAIT} from './constants';

import './App.css';
import ErrorDialogComponent from './components/ErrorDialogComponent';
import { AppStateContext } from './AppLogic';
import MessageComponent from './components/MessageComponent';

export const AppComponent: FunctionComponent = () => {
  
  const { appState, executeAction } = useContext(AppStateContext)

  useEffect( () => {
    executeAction({ type : ACTION_CHECK_DEFAULT_USER,
      finishFunction : () => (true) });
    executeAction( { type : ACTION_FETCH_ALL_AWAIT,
      finishFunction : () => (true) })
  }, []);

  const isServerActionInProgress = appState.systemStore.value.serverActionInProgress == true;

  const doRefresh =  () => {
    // need a finish function to have ServerActionInProgress set correctly.
    executeAction({ type : ACTION_FETCH_ALL_AWAIT,
      finishFunction : () => (true) })
  }  

  const deleteAll = () => {
    if (isServerActionInProgress) {
      console.log("Delete or Refresh in progress - ignore");
      return;
    }
    // we need a finish-function to make the pushAction recognise this
    // as something to wait on! (sets and unsets "isServerActionInProgress" in appState.systemStore)
    executeAction( { type : ACTION_DELETE_ALL ,
        finishFunction : () => (true) } ) 
  }

  const hasErrors = (appState.systemStore.value.errors != null && 
                     appState.systemStore.value.errors.length > 0)

  const message = hasErrors ? null : appState.systemStore.value.message;

  const deleteStyle = "text-align: right; margin-left: 10px;" +
    (isServerActionInProgress ? "color: grey; cursor: not-allowed;" : "cursor:pointer;")

  return (
    <div>
      <MessageComponent message={message} />
      <ErrorDialogComponent
          isOpen={hasErrors} 
          error={appState.systemStore.value.errors[0]} onClose={() => {}} />
    <div className="grid-container">
      <header className="header">   
        <h1 >Pizza 1337</h1>
        <div>
        <button className="refresh-button" disabled={isServerActionInProgress} 
            onClick={() => doRefresh() }>
          🔄 Refresh
        </button>
        <a style={deleteStyle} onClick={ () => deleteAll()}>&#128465;</a>
        </div>
      </header>
      <div className="orders scrollable-pane">
        <OrderListComponent />
      </div>
      <div className="pizza-types scrollable-pane">
        <PizzaTypesListComponent />
      </div>
      <div className="doughs scrollable-pane">
        <DoughListComponent />
      </div>
        <div className="toppings scrollable-pane">
        <ToppingsListComponent />
      </div>
      <div className="beverages scrollable-pane">
        <BeveragesListComponent />
      </div>
    </div>
    </div>      
    );
};