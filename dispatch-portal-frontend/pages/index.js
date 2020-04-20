import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import PropTypes from 'prop-types';
import DataTable from 'react-data-table-component';
import { dispatchService } from '../services/dispatch/dispatch.service';
import { privateRoute } from '../components/privateRoute/PrivateRoute';
import Menu from '../components/menu/Menu';
import Loading from '../components/loading/Loading';
import { config } from '../config/config';
import { Routes } from '../config/routes';

const columns = [
  {
    name: ' ',
    selector: 'color',
    sortable: true,
    cell: row => (
      <span className={row.system === 'LIT' ? 'lit-row' : 'cts-row'} />
    )
  },
  {
    name: 'System',
    selector: 'system',
    sortable: true
  },
  {
    name: 'Dispatch ID', // Todo: link to...
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
    selector: 'customerLocation',
    sortable: true
  },
  {
    name: 'Bruin Ticket ID', // Todo: link to...
    selector: 'bruinTicketId',
    sortable: true
  },
  {
    name: 'Time Scheduled',
    selector: 'timeScheduled',
    sortable: true
  },
  {
    name: 'Dispatch Status',
    selector: 'status',
    sortable: true,
    cell: row => (
      <button type="button" className={row.status.replace(' ', '_')}>
        {row.status}
      </button>
    )
  }
];

function Index({ authToken }) {
  const [page, setPage] = useState(1);
  const [data, setData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function getAllDispatches() {
      const response = await dispatchService.getAll();
      setData(response.data);
      setIsLoading(false);
    }
    getAllDispatches();
  }, [page]);

  return (
    <div>
      <Menu authToken={authToken} />
      <Link href={Routes.NEW_DISPATCH()}>
        <button className="new" type="button">
          Create new dispatch
        </button>
      </Link>
      {isLoading ? (
        <Loading />
      ) : (
        <DataTable
          title="Dispatches List"
          columns={columns}
          data={data}
          fixedHeader
          pagination
          className="dataTable"
        />
      )}
    </div>
  );
}

Index.propTypes = {
  authToken: PropTypes.string
};

export default privateRoute(Index);
