export const locationInAdapter = data => ({
  owner: data.client_name,
  address1: data.client_address.address,
  country: data.client_address.country,
  city: data.client_address.city,
  state: data.client_address.state,
  zip: data.client_address.zip
});
