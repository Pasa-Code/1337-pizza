import { h } from 'preact';

interface MessageProperties {
  message: string | null
}
const MessageComponent = ( props: MessageProperties) => {

  if (!props.message) return null;

  return (
    <div class="dialog-overlay">
      <div class="dialog-content card">
        <h2>Message</h2>
            {props.message}
      </div>
    </div>
  );
};

export default MessageComponent;
