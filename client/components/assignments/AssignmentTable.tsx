import { DataGrid, GridCellParams, GridColDef, GridRowSelectionModel, GridValueGetterParams, gridColumnsTotalWidthSelector } from '@mui/x-data-grid';
import { Assignment } from "./AssignmentTypes";
import { Switch } from '@mui/material';
import { useState } from 'react';

export default function AssignmentTable({ assignments, setSelectedAssignments, toggleAssignmentActive }: { assignments: Assignment[], setSelectedAssignments: React.Dispatch<React.SetStateAction<Assignment[]>>, toggleAssignmentActive: (assignment: Assignment) => void }) {
    const [rowSelectionModel, setRowSelectionModel] = useState<GridRowSelectionModel>([]);

    const columns: GridColDef[] = [
        { field: 'assignmentTitle', headerName: 'Title', flex: 3 },
        { field: 'className', headerName: 'Class', flex: 2 },
        {
            field: 'dueDate',
            headerName: 'Due Date',
            flex: 2,
            valueGetter: (params: GridValueGetterParams) => { return new Date(params.row.dueDate).toLocaleDateString('en-US', { year: 'numeric', month: '2-digit', day: '2-digit', timeZone: 'UTC' }) },
        },
        {
            field: 'lastScan',
            headerName: 'Last Scan',
            flex: 2,
            valueGetter: (params: GridValueGetterParams) => { return params.row.lastScan ? new Date(params.row.lastScan).toLocaleDateString('en-US', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit', timeZone: 'EST' }) : 'not yet scanned.' },
        },
        {
            field: 'assignmentActive',
            headerName: 'Active',
            flex: 1,
            align: 'center',
            headerAlign: 'center',
            renderCell: (params: GridCellParams) => {
                return (
                    <Switch checked={params.row.assignmentActive} onChange={() => { toggleAssignmentActive(params.row as Assignment); }} onClick={e => e.stopPropagation()} />
                );
            }
        },
    ];
    const rows = (assignments || []).map((assignment, index) => ({
        id: index + 1,
        ...assignment,
    }));

    return (
        <DataGrid
            checkboxSelection
            rows={rows}
            columns={columns}
            initialState={{
                pagination: {
                    paginationModel: { page: 0, pageSize: 5 },
                },
            }}
            pageSizeOptions={[5, 10]}
            onRowSelectionModelChange={(newRowSelectionModel) => {
                setRowSelectionModel(newRowSelectionModel);
                const selectedAssignments = assignments.filter((_, index) => newRowSelectionModel.includes(index + 1));
                setSelectedAssignments(selectedAssignments)
            }}
            rowSelectionModel={rowSelectionModel}
        />
    );
}