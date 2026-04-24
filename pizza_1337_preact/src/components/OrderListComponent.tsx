import { h, FunctionComponent } from 'preact';
import { useContext, useState } from 'preact/hooks';
import { OrderComponent } from './OrderComponent';
import CreateOrderDialog from './CreateOrderDialog';
import { ACTION_DELETE_ORDERS_AND_FETCH, 
  ACTION_FETCH_ORDER_CREATE_DATA} from '../constants';
import { AppStateContext } from '../AppLogic';

export const OrderListComponent : FunctionComponent = ( ) => {
 
  const { appState, executeAction } = useContext(AppStateContext)
  
  const [ isOrderCreateDialogOpen , setIsOrderCreateDialogOpen] = useState(false);

  const isServerActionInProgress = appState.systemStore.value.serverActionInProgress == true;
  
  const { orders, loading, error } = appState.pizzaOrdersStore.value;

  const openOrderCreateDialog = () => {
      executeAction({ type : ACTION_FETCH_ORDER_CREATE_DATA,
          finishFunction : () => {
            setIsOrderCreateDialogOpen(true) }
       });
  }

  const deleteAllOrders = () => {
    if (isServerActionInProgress) {
      console.log("Delete all Orders in progress ... ignoring.")
      return;
    }
    executeAction( { type : ACTION_DELETE_ORDERS_AND_FETCH, 
      payload : { orderIds : Object.keys(orders) },
      finishFunction : () => (true) })
  }

  if (error) return <div>Error: {error}</div>;

  const deleteStyle = "margin-left: 10px;" + 
    (isServerActionInProgress ? "color: grey; cursor: not-allowed;" : "cursor: pointer;");

  return (
    <div>
      <CreateOrderDialog 
        data-testid="create-order-dialog"
        isOpen={isOrderCreateDialogOpen}
        onClose={() => setIsOrderCreateDialogOpen(false)}
        />
        
      <div style="display: flex; justify-content: space-between; align-items: center;">
            <h2>Orders</h2>
            <div>
            <button disabled={isServerActionInProgress} 
              onClick={() => openOrderCreateDialog()}>Create</button>
            <a style={deleteStyle} onClick={() => deleteAllOrders()}>&#128465;</a>
            </div>
      </div>   
      <div className="spinner-container" >
        {loading && (
        <div className="spinner-overlay" data-testid="loading-overlay">
          <div className="spinner"></div>
        </div>
        )}  
        <div className="order-grid-container">
          {Object.keys(orders).map( orderId => 
            <OrderComponent 
              order={orders[orderId]}  />)}  
        </div>
      </div>
    </div>

  );
};