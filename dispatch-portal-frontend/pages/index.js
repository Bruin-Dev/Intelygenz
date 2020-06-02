import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import PropTypes from 'prop-types';
import DataTable from 'react-data-table-component';
import { dispatchService } from '../services/dispatch/dispatch.service';
import { privateRoute } from '../components/privateRoute/PrivateRoute';
import Menu from '../components/menu/Menu';
import { StatusButton } from '../ui/components/status/StatusButton';
import { Routes } from '../config/routes';
import { config } from '../config/config';
import './index.scss';

const columns = [
  {
    name: ' ',
    selector: 'color',
    cell: row => (
      <span
        className={
          row.vendor.toUpperCase() === config.VENDORS.CTS
            ? 'cts-row'
            : 'lit-row'
        }
      />
    )
  },
  {
    name: 'System',
    selector: 'vendor',
    sortable: true,
    cell: row => <span>{row.vendor.toUpperCase()}</span>
  },
  {
    name: 'Dispatch ID',
    selector: 'id',
    sortable: true,
    cell: row => (
      <a className="link" href={`${Routes.DISPATCH()}/${row.id}`}>
        {row.id}
      </a>
    )
  },
  {
    name: 'Customer/Location',
    cell: row => (
      <span>{`${row.onSiteContact.street} ${row.onSiteContact.city} ${row.onSiteContact.state} ${row.onSiteContact.zip}`}</span>
    )
  },
  {
    name: 'Bruin Ticket ID',
    selector: 'mettelId',
    sortable: true
  },
  {
    name: 'Time Scheduled',
    selector: 'dateDispatch',
    sortable: true
  },
  {
    name: 'Dispatch Status',
    selector: 'dispatch_status',
    sortable: true,
    cell: row => <StatusButton status={row.status} />
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

      {apiError && <p>Error!</p>}

      <DataTable
        title="Dispatches List"
        columns={columns}
        data={data}
        fixedHeader
        pagination
        progressPending={isLoading}
        className="dataTable"
      />
    </div>
  );
}

Index.propTypes = {
  authToken: PropTypes.string
};

export default privateRoute(Index);
