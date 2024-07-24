import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [consumerNumber, setConsumerNumber] = useState('');
  const [image, setImage] = useState(null);
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('consumer_number', consumerNumber);
    formData.append('meter_image', image);

    try {
      const response = await axios.post('http://localhost:5000/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setResult(response.data);
    } catch (error) {
      console.error('Error uploading image:', error);
    }
  };

  return (
    <div className="App">
      <h1>KSEB Billing App</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="consumerNumber">Consumer Number:</label>
          <input
            type="text"
            id="consumerNumber"
            value={consumerNumber}
            onChange={(e) => setConsumerNumber(e.target.value)}
            required
          />
        </div>
        <div>
          <label htmlFor="meterImage">Meter Reading Image:</label>
          <input
            type="file"
            id="meterImage"
            onChange={(e) => setImage(e.target.files[0])}
            accept="image/*"
            required
          />
        </div>
        <button type="submit">Submit</button>
      </form>
      {result && (
        <div>
          <h2>Result</h2>
          <p>Consumer Number: {result.consumer_number}</p>
          <p>Reading: {result.reading} kWh</p>
          <p>Bill Amount: ₹{parseFloat(result.bill_amount).toFixed(2)}</p>
          <a href={`https://bills.kseb.in/`} target="_blank" rel="noopener noreferrer">
            Verify on KSEB Website
          </a>
        </div>
      )}
    </div>
  );
}

export default App;
