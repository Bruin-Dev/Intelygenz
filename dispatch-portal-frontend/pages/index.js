import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import PropTypes from 'prop-types';
import DataTable from 'react-data-table-component';
import { useRouter } from 'next/router';
import debounce from 'lodash.debounce';
import { DispatchService } from '../services/dispatch/dispatch.service';
import { privateRoute } from '../components/privateRoute/PrivateRoute';
import Menu from '../components/menu/Menu';
import { StatusButton } from '../ui/components/status/StatusButton';
import { getTimeZoneShortName } from '../config/constants/dispatch.constants';
import { Routes } from '../config/routes';
import { config } from '../config/config';
import './index.scss';

const columns = [
  {
    name: '',
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
    name: 'Bruin Ticket ID',
    selector: 'mettelId',
    sortable: true
  },
  {
    name: 'Customer/Location',
    cell: row => (
      <span>{`${row.onSiteContact.street} ${row.onSiteContact.city} ${row.onSiteContact.state} ${row.onSiteContact.zip}`}</span>
    )
  },
  {
    name: 'Vendor',
    selector: 'vendor',
    sortable: true,
    cell: row => <span>{row.vendor.toUpperCase()}</span>
  },
  {
    name: 'Vendor Dispatch ID',
    selector: 'id',
    sortable: true, // Todo: delete uppercase
    cell: row => (
      <a
        className="link"
        data-test-id={`dispatchId-${row.id}-link`}
        href={`${Routes.DISPATCH()}/${row.id}?vendor=${
          row.vendor === config.VENDORS.CTS
            ? config.VENDORS.CTS
            : config.VENDORS.LIT
        }`}
      >
        {row.id}
      </a>
    )
  },
  {
    name: 'Scheduled Time',
    selector: 'dateDispatch',
    sortable: true,
    cell: row => (
      <span>{`${row.dateDispatch} ${row.timeDispatch} ${getTimeZoneShortName(
        row.timeZone
      )}`}</span>
    )
  },
  {
    name: 'Dispatch Status',
    selector: 'status',
    sortable: true,
    cell: row => <StatusButton status={row.status} />
  }
];

function Index({ authToken }) {
  const router = useRouter();
  const [page, setPage] = useState(1);
  const [data, setData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [apiError, setApiError] = useState(false);
  const [searchData, setSearchData] = useState(false);
  const [paramBySearch, setParamBySearch] = useState('id');

  const getAllDispatches = async () => {
    setIsLoading(true);
    setApiError(false);

    const response = await new DispatchService().getAll();

    if (response && response.data) {
      setData(response.data);
    }

    if (response && response.error) {
      setApiError(response.error);
    }
    setIsLoading(false);
  };

  useEffect(() => {
    getAllDispatches();
  }, [page]);

  const searchDispatch = debounce(textSearch => {
    let auxdata = [...data];
    auxdata = auxdata.filter(obj => obj[paramBySearch].search(textSearch) > -1);
    setSearchData(auxdata);
  }, 300);

  return (
    <div data-testid="index-page-component">
      <Menu authToken={authToken} />

      <div className="flex flex-col px-10">
        <div>
          <Link href={Routes.NEW_DISPATCH()}>
            <button
              type="button"
              className="float-right bg-transparent hover:bg-teal-500 text-teal-700 hover:text-white py-2 px-4 m-4 border border-teal-500 hover:border-transparent rounded"
            >
              Create new dispatch
            </button>
          </Link>
        </div>

        <div className="flex flex-grow">
          <h1 className="text-2xl px-3">Dispatches List</h1>
          {apiError && (
            <button
              type="button"
              onClick={getAllDispatches}
              className="float-center text-red-500 border border-red-500 text-sm px-1 m-2 rounded inline-flex items-center"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                width="16"
                height="16"
                className="fill-current w-4 h-4 mr-1"
              >
                <path
                  className="heroicon-ui"
                  d="M6 18.7V21a1 1 0 0 1-2 0v-5a1 1 0 0 1 1-1h5a1 1 0 1 1 0 2H7.1A7 7 0 0 0 19 12a1 1 0 1 1 2 0 9 9 0 0 1-15 6.7zM18 5.3V3a1 1 0 0 1 2 0v5a1 1 0 0 1-1 1h-5a1 1 0 0 1 0-2h2.9A7 7 0 0 0 5 12a1 1 0 1 1-2 0 9 9 0 0 1 15-6.7z"
                />
              </svg>
              There are problems obtaining one or more suppliers, click to
              reload.
            </button>
          )}
        </div>

        <div className=" bg-white rounded flex items-center w-full p-3 shadow-sm border border-gray-200">
          <button type="button" className="outline-none focus:outline-none">
            <svg
              className=" w-5 text-gray-600 h-5 cursor-pointer"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
            </svg>
          </button>
          <input
            type="search"
            onChange={e => searchDispatch(e.target.value)}
            placeholder="Search for..."
            className="w-full pl-4 text-sm outline-none focus:outline-none bg-transparent"
          />
          <div className="select">
            <select
              className="text-sm outline-none focus:outline-none bg-transparent"
              onChange={e => setParamBySearch(e.target.value)}
            >
              <option value="id" selected>
                Vendor Dispatch ID
              </option>
              <option value="mettelId">Bruin Ticket ID</option>
              <option value="vendor">Vendor</option>
              <option value="dataDispatch">Scheduled Time</option>
              <option value="status">Dispatch Status</option>
            </select>
          </div>
        </div>

        <DataTable
          columns={columns}
          data={searchData || data}
          fixedHeader
          pagination
          progressPending={isLoading}
          className="dataTable"
          defaultSortField="dateDispatch"
          defaultSortAsc={false}
          onRowClicked={rowData =>
            router.push(
              `${Routes.DISPATCH()}/${rowData.id}?vendor=${rowData.vendor}`
            )
          }
        />
      </div>
    </div>
  );
}

Index.propTypes = {
  authToken: PropTypes.string
};

export default privateRoute(Index);
