import Header from "@/components/Header";
import Box from '@mui/material/Box';
import CssBaseline from '@mui/material/CssBaseline';
import DefaultLayout from "../components/DefaultLayout";
import Container from '@mui/material/Container';
import Paper from "@mui/material/Paper";
import { useEffect, useState } from "react";
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import { Button, Checkbox, Dialog, FormControlLabel, Typography } from "@mui/material";
import dayjs from 'dayjs';
import TextField from '@mui/material/TextField';
import { FormControl, FormLabel } from '@mui/material';
import { DatePicker } from "@mui/x-date-pickers";
import { useAuth } from "@/components/AuthProvider";
import { useRouter } from "next/router";
import Table from '@mui/material/Table';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';


export default function Dashboard() {
    const [result, setResult] = useState([]);
    const [filterResult, setFilterResult] = useState([]);
    const [open, setOpen] = useState(false);
    const handleOpen = () => setOpen(true);
    const handleClose = () => setOpen(false);
    const [scanNum, setScanNum] = useState(0);
    const [numAssignment, setNumberAssignments] = useState(0);
    const [classes, setClasses] = useState([])
    const [date, setDate] = useState(dayjs(new Date()))
    const [classesFilter, setClassesFilter] = useState([])
    const [isDirty, setIsDirty] = useState(false);
    const [keyword, setKeyword] = useState("");
    const router = useRouter();

    useEffect(() => {
        const fetchData = async () => {
          try {
            async function getNumberAssignment() {
              let response = await fetch('/api/assignments/');
              response = await response.json();
              setNumberAssignments(response.length);
            }
      
            async function getScanResults() {
              await getNumberAssignment();
              let response = await fetch('/api/results/');
              response = await response.json();
      
              let numberSuccessfulScans = 0;
              let classNames = new Set();
              for (let i = 0; i < response.length; i += 1) {
                let curr = response[i];
                classNames.add(curr.assignment.courseName);
              }
      
              classNames = Array.from(classNames);
      
              setClasses([...classNames]);
              setClassesFilter([...classNames]);
              setResult(response);
              setFilterResult(response);
              setScanNum(response.length);
              setSuccessfulScans(numberSuccessfulScans);
            }
      
            await getScanResults();
          } catch (error) {
            console.error('Error in fetchData:', error);
            // Handle the error, log it, or perform other actions
          }
        };
      
        fetchData();
      }, []);



    const closed = () => {
        setFilterResult(result.filter(item => {
            return classesFilter.includes(item.assignment.courseName) && date.diff(dayjs(new Date(item.assignment.dueDate))) >= 0 && item.assignment.title.includes(keyword)
        }))

        setClassesFilter(classes)
        handleClose()
    }

    const checkBoxChange = (e, entry) => {
        if (e.target.checked) {
            let newArray = [...classesFilter, entry]
            console.log(newArray)
            setClassesFilter(newArray)
            setIsDirty(false);
        }

        else {
            let newClasses = classesFilter.filter(item => item !== entry);
            setClassesFilter([...newClasses])
            if (newClasses.length <= 0) {
                setIsDirty(true);
                return;
            }
            console.log(newClasses)
        }
    }

    return (
        <DefaultLayout>
            <div>
                <Dialog open={open} onClose={handleClose}>
                    <DialogTitle>Filter</DialogTitle>
                    <DialogContent>
                        <DialogContentText id="alert-dialog-description">
                            <FormControl>
                                <FormLabel>Classes</FormLabel>
                                {
                                    classes?.map((entry, index) =>
                                        <FormControlLabel control={<Checkbox defaultChecked />} label={entry} onChange={(e) => checkBoxChange(e, entry)} />
                                    )
                                }
                                <FormLabel>Keywords</FormLabel>
                                <TextField id="outlined-basic" style={{ marginBottom: 20 }} variant="outlined" defaultValue={keyword} onChange={(e) => setKeyword(e.target.value)} />
                                <FormLabel>Due Date Before (Inclusive)</FormLabel>
                                <DatePicker defaultValue={date} onChange={(v) => setDate(dayjs(new Date(v)))} />
                                <Button disabled={isDirty} style={{ marginTop: 10 }} variant="contained" onClick={closed} autoFocus>
                                    Close
                                </Button>
                            </FormControl>
                        </DialogContentText>
                    </DialogContent>
                    <DialogActions>
                    </DialogActions>
                </Dialog>
                <Container component="main">
                    <CssBaseline />
                    <Box
                        sx={{
                            marginTop: 8,
                            display: 'flex',
                            flexDirection: 'row',
                            alignItems: 'center',
                            justifyContent: "space-evenly"
                        }}
                    >
                        <div style={{ textAlign: "center", justifyContent: "center", alignItems: "center" }}>
                            <div style={{ borderRadius: "100px", border: "10px solid #cc0000", height: 200, width: 200, display: "flex", textAlign: "center", justifyContent: "center", alignItems: "center" }}>
                                <Typography style={{ fontSize: 60 }}>{scanNum}</Typography>
                            </div>
                            <Typography style={{ marginTop: 20, fontWeight: "bold", fontSize: 15 }}>Scan Results</Typography>
                        </div>

                        <div style={{ textAlign: "center", justifyContent: "center", alignItems: "center" }}>
                            <div style={{ borderRadius: "100px", border: "10px solid #cc0000", height: 200, width: 200, display: "flex", textAlign: "center", justifyContent: "center", alignItems: "center" }}>
                                <Typography style={{ fontSize: 60 }}>{numAssignment}</Typography>
                            </div>
                            <Typography style={{ marginTop: 20, fontWeight: "bold", fontSize: 15 }}>Assignments</Typography>
                        </div>
                    </Box>

                    <Box
                        sx={{
                            marginTop: 8,
                            display: 'flex',
                            flexDirection: 'row-reverse',
                        }}
                    >

                        <Button variant="contained" onClick={handleOpen}>Filter</Button>
                    </Box>
                    <Box
                        sx={{
                            marginTop: 8,
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                        }}
                    >
                        <TableContainer component={Paper}>
                            <Table sx={{ minWidth: 850, border : 1, borderStyle : "solid" }} aria-label="simple table">
                                <TableHead>
                                    <TableRow>
                                        <TableCell style={{fontWeight: "bold"}}>Assignment Name</TableCell>
                                        <TableCell style={{fontWeight: "bold"}} align="right">Course Name</TableCell>
                                        <TableCell style={{fontWeight: "bold"}} align="right">Due Date</TableCell>
                                        <TableCell style={{fontWeight: "bold"}} align="right">Confidence</TableCell>
                                        <TableCell style={{fontWeight: "bold"}} align="right">Url</TableCell>
                                    </TableRow>
                                    {
                                        filterResult?.map((entry, index) =>
                                            <TableRow>
                                                <TableCell >{entry.assignment.title}</TableCell>
                                                <TableCell align="right">{entry.assignment.courseName}</TableCell>
                                                <TableCell align="right">{new Date(entry.assignment.dueDate).toDateString()}</TableCell>
                                                <TableCell align="right">{entry.confidenceProbability.toFixed(2)}%</TableCell>
                                                <TableCell align="right">
                                                    <a href={`${entry.url}`}>
                                                        <Typography>Site Link</Typography>
                                                    </a>
                                                </TableCell>
                                            </TableRow>
                                        )
                                    }
                                </TableHead>
                            </Table>
                        </TableContainer>
                    </Box>
                </Container>
            </div>
        </DefaultLayout>
    )
}