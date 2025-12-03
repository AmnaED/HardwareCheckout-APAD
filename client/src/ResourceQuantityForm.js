import React, {useState} from "react";
import './Resource.css'

function ResourceQuantityForm(props) {
  const [formData, setFormData] = useState({
    Quantity: '',
  });

return (
  <div>
   <table id = "table1">
    <tr>
      <th></th>
      <th>Quantity</th>
    </tr>
    <tr>
      <td>Hardware #1</td>
      <td class = "text-outline-box">{props.quantity1}</td>
    </tr>
    <tr>
      <td>Hardware #2</td>
      <td class = "text-outline-box">{props.quantity2}</td>
    </tr>
  </table>
  </div>

  /*Quantity from database would be inserted in box*/
)
}
export default ResourceQuantityForm; 