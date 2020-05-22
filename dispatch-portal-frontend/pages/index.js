import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import PropTypes from 'prop-types';
import DataTable from 'react-data-table-component';
import { dispatchService } from '../services/dispatch/dispatch.service';
import { privateRoute } from '../components/privateRoute/PrivateRoute';
import Menu from '../components/menu/Menu';
import Loading from '../components/loading/Loading';
import { Routes } from '../config/routes';
import { config } from '../config/config';

const columns = [
  {
    name: ' ',
    selector: 'color',
    sortable: true,
    cell: row => (
      <span
        className={row.vendor === config.VENDORS.CTS ? 'cts-row' : 'lit-row'}
      />
    )
  },
  {
    name: 'System',
    selector: 'vendor',
    sortable: true
  },
  {
    name: 'Dispatch ID',
    selector: 'dispatch_number',
    sortable: true,
    cell: row => (
      <a className="link" href={`${Routes.DISPATCH()}/${row.dispatch_number}`}>
        {row.dispatch_number}
      </a>
    )
  },
  {
    name: 'Customer/Location',
    selector: 'customerLocation',
    sortable: true,
    cell: row => (
      <span>{`${row.job_site_street} ${row.job_site_city} ${row.job_site_state} ${row.job_site_zip_code}`}</span>
    )
  },
  {
    name: 'Bruin Ticket ID',
    selector: 'mettel_bruin_ticket_id',
    sortable: true
  },
  {
    name: 'Time Scheduled',
    selector: 'date_of_dispatch',
    sortable: true
  },
  {
    name: 'Dispatch Status',
    selector: 'dispatch_status',
    sortable: true,
    cell: (
      row // Todo: review status states
    ) => (
      <button type="button" className={row.dispatch_status.replace(' ', '_')}>
        {row.dispatch_status}
      </button>
    )
  }
];

function Index({ authToken }) {
  const [page, setPage] = useState(1);
  const [data, setData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [apiError, setApiError] = useState(false);

  useEffect(() => {
    async function getAllDispatches() {
      const response = await dispatchService.getAll();
      if (response && response.data) {
        setData(response.data);
      }

      if (response && response.error) {
        setApiError(response.error);
      }
      setIsLoading(false);
    }
    getAllDispatches();
  }, [page]);

  return (
    <div>
      <Menu authToken={authToken} />
      <Link href={Routes.NEW_DISPATCH()}>
        <button
          type="button"
          className="float-right bg-transparent hover:bg-teal-500 text-teal-700 hover:text-white py-2 px-4 m-4 border border-teal-500 hover:border-transparent rounded"
        >
          Create new dispatch
        </button>
      </Link>
      {isLoading && <Loading />}

      {apiError && <p>Error!</p>}

      <DataTable
        title="Dispatches List"
        columns={columns}
        data={data}
        fixedHeader
        pagination
        className="dataTable"
      />
    </div>
  );
}

Index.propTypes = {
  authToken: PropTypes.string
};

export default privateRoute(Index);
