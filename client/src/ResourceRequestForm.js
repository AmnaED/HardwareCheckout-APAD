import React, { useState, useEffect } from "react";
import './Resource.css';

const API_BASE_URL = "http://localhost:5001";


function ResourceRequestForm({ projectID }) {
  const [formData, setFormData] = useState({
    requestAmount1: '',
    requestAmount2: ''
  });

  const [hardwareData, setHardwareData] = useState({
    capacity1: '',
    available1: '',
    capacity2: '',
    available2: ''
  });

  // Extract fetch logic
  async function fetchHardwareData() {
    try {

     const res1Cap = await fetch(`${API_BASE_URL}/hardware/1/capacity`);
     const res1Avail = await fetch(`${API_BASE_URL}/hardware/1/availability`);
     const res2Cap = await fetch(`${API_BASE_URL}/hardware/2/capacity`);
     const res2Avail = await fetch(`${API_BASE_URL}/hardware/2/availability`);
     // const res1Cap = await fetch("http://127.0.0.1:5000/hardware/1/capacity");
     // const res1Avail = await fetch("http://127.0.0.1:5000/hardware/1/availability");
     // const res2Cap = await fetch("http://127.0.0.1:5000/hardware/2/capacity");
     // const res2Avail = await fetch("http://127.0.0.1:5000/hardware/2/availability");

      const cap1 = await res1Cap.json();
      const avail1 = await res1Avail.json();
      const cap2 = await res2Cap.json();
      const avail2 = await res2Avail.json();

        setHardwareData({
            capacity1: cap1.capacity[1],
            available1: avail1.availability[1],
            capacity2: cap2.capacity[2],
            available2: avail2.availability[2]
        });

    } catch (error) {
      console.error("Error fetching hardware data:", error);
      alert("Failed to load hardware data");
    }
  }

  useEffect(() => {
    fetchHardwareData();
  }, []);

  function handleInputChange(event) {
    const { name, value } = event.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  }
  async function handleSubmit(event, type) {
    event.preventDefault();
    const route = type === 'checkin' ? 'checkin' : 'checkout';

    try {
      const requests = [];

      if (formData.requestAmount1) {
        requests.push(
          fetch(`${API_BASE_URL}/hardware/${route}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({
              qty: parseInt(formData.requestAmount1),
              project_id: parseInt(projectID),
              hardware_id: 1,
            }),
          })
        );
      }

      if (formData.requestAmount2) {
        requests.push(
          fetch(`${API_BASE_URL}/hardware/${route}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({
              qty: parseInt(formData.requestAmount2),
              project_id: parseInt(projectID),
              hardware_id: 2,
            }),
          })
        );
      }
    
      const responses = await Promise.all(requests);

        const results = await Promise.all(responses.map((res) => res.json()));

        let successMessages = [];
        let errorMessages = [];

        for (let i = 0; i < responses.length; i++) {
        const res = responses[i];
        const result = results[i];

        if (!res.ok) {
            errorMessages.push(`Hardware #${i + 1}: ${result.error || "Unknown error"}`);
        } else if (result.message) {
            successMessages.push(`Hardware #${i + 1}: ${result.message}`);
        } else {
            successMessages.push(`Hardware #${i + 1}: ${type} successful`);
        }
        }

        if (errorMessages.length > 0) {
        alert(errorMessages.join("\n"));
        }
        if (successMessages.length > 0) {
        alert(successMessages.join("\n"));
        }
      // Clear input fields
      setFormData({ requestAmount1: '', requestAmount2: '' });

      // **Reload hardware availability**
      await fetchHardwareData();
    

    } catch (error) {
      console.error("Error submitting hardware request:", error);
      alert("Hardware request failed");
    }
      
  }
  return (
    <form>
      <div>
        <table id="table1">
          <thead>
            <tr>
              <th className="custom-padding"></th>
              <th className="custom-padding">Total Capacity</th>
              <th className="custom-padding">Currently Available</th>
              <th className="custom-padding">Request Amount</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Hardware #1</td>
              <td className="text-outline-box">{hardwareData.capacity1}</td>
              <td className="text-outline-box">{hardwareData.available1}</td>
              <td className="text-outline-box">
                <input type="text" name="requestAmount1" value={formData.requestAmount1} onChange={handleInputChange} />
              </td>
            </tr>
            <tr>
              <td>Hardware #2</td>
              <td className="text-outline-box">{hardwareData.capacity2}</td>
              <td className="text-outline-box">{hardwareData.available2}</td>
              <td className="text-outline-box">
                <input type="text" name="requestAmount2" value={formData.requestAmount2} onChange={handleInputChange} />
              </td>
            </tr>
          </tbody>
        </table>

        <button type="button" onClick={(e) => handleSubmit(e, 'checkin')}>Check-In</button>
        <button type="button" onClick={(e) => handleSubmit(e, 'checkout')}>Check-Out</button>
      </div>
    </form>
  );
}

export default ResourceRequestForm;
