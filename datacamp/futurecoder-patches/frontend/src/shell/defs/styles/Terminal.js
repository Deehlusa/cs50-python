
export default {
  container: {
    minWidth: '500px',
    minHeight: '300px',
    maxWidth: '100%', // Fill parent before overflowing
    maxHeight: '100%', // Fill parent before overflowing
    borderRadius: '0',
    overflow: 'auto',
    cursor: 'text',
    background: '#0d0f14',
    backgroundSize: 'cover'
  },
  content: {
    padding: '42px 20px 20px 20px',
    height: '100%',
    fontSize: '15px',
    color: '#e7e9ee',
    fontFamily: 'monospace'
  },
  inputArea: {
    display: 'inline-block',
    width: 'calc(100% - 2.5em)'
  },
  promptLabel: {
    color: '#7c5cff'
  },
  input: {
    border: '0',
    padding: '0',
    margin: '0',
    marginBottom: '2em',
    width: '100%',
    background: 'transparent',
    fontSize: '15px',
    color: '#FFFFFF',
    fontFamily: 'monospace',
    outline: 'none' // Fix for outline showing up on some browsers
  }
}
