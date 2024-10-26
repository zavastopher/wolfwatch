import * as React from "react";
import {
    AppBar,
    Box,
    Toolbar,
    IconButton,
    Badge,
    MenuItem,
    Menu,
    Avatar,
    Divider,
    ListItemIcon,
    Table,
    TableCell,
    TableRow,
    Typography,
} from "@mui/material";
import {
    Assignment,
    Logout,
    Settings,
    Notifications,
    AccountCircle,
} from "@mui/icons-material";
import { useAuth } from "./AuthProvider";
import Link from "next/link";
import { useEffect } from "react";
import TableContainer from '@mui/material/TableContainer'; 
import Paper from "@mui/material/Paper"; 

export default function Header() {
    const { logout, identity } = useAuth();
    const [badge, setBadge] = React.useState(0);
    const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
    const [anchorNotificationEl, setNotificationAnchorEl] = React.useState<null | HTMLElement>(null);
    const [results, setResults] = React.useState([]);
    const open = Boolean(anchorEl);
    const notificationOpen = Boolean(anchorNotificationEl);
    const handleClick = (event: React.MouseEvent<HTMLElement>) => {
        setAnchorEl(event.currentTarget);
    };
    const handleClose = () => {
        setAnchorEl(null);
    };


    const handleNotificationClick = (event: React.MouseEvent<HTMLElement>) => {
        setNotificationAnchorEl(event.currentTarget);
    };
    const handleNotificationClose = () => {
        for(let i = 0; i < results.length; i += 1) { 
            let curr = results[i]; 
            const lastLogin = identity?.lastLogin
            const otherDate = curr.assignment.lastNotificationCheck 

            if(new Date(lastLogin) <= new Date(otherDate)) {

                curr.isSeen = false 
            }
        }
        setResults([...results])
        setNotificationAnchorEl(null);
        setBadge(0);  
    };


    useEffect(() => {
        const fetchData = async () => {
          try {
            let response = await fetch('/api/results/');
            response = await response.json();
      
            let total = 0;
            for (let i = 0; i < response.length; i += 1) {
              let curr = response[i];
              const lastLogin = identity?.lastLogin;
              const otherDate = curr.assignment.lastNotificationCheck;
      
              if (new Date(lastLogin) <= new Date(otherDate)) {
                total += 1;
                curr.isSeen = true;
              }
            }
      
            setResults(response);
            setBadge(total);
          } catch (error) {
            // Handle errors, log them, or perform other actions
            console.error('Error fetching data:', error);
          }
        };
      
        fetchData();
      }, [identity]);

    const menu = (
        <Menu
            anchorEl={anchorEl}
            id="account-menu"
            open={open}
            onClose={handleClose}
            onClick={handleClose}
            transformOrigin={{ horizontal: "right", vertical: "top" }}
            anchorOrigin={{ horizontal: "right", vertical: "bottom" }}
        >
            <MenuItem>
                <Avatar sx={{ bgcolor: "#ef4444", marginRight: "10px" }}>
                    {
                        identity &&
                        identity?.firstName?.charAt(0) + identity?.lastName?.charAt(0)
                    }
                </Avatar>
                {identity?.firstName} {identity?.lastName}
            </MenuItem>
            <MenuItem>
                <Link
                    href="/assignments"
                    style={{
                        textDecoration: "none",
                        color: "black",
                        alignItems: "center",
                        display: "flex",
                    }}
                >
                    <ListItemIcon>
                        <Assignment />
                    </ListItemIcon>
                    Assignments
                </Link>
            </MenuItem>
            <Divider />
            <MenuItem>
                <Link
                    href="/settings"
                    style={{
                        textDecoration: "none",
                        color: "black",
                        alignItems: "center",
                        display: "flex",
                    }}
                >
                    <ListItemIcon>
                        <Settings fontSize="small" />
                    </ListItemIcon>
                    Settings
                </Link>
            </MenuItem>
            <MenuItem onClick={() => logout()}>
                <ListItemIcon>
                    <Logout fontSize="small" />
                </ListItemIcon>
                Logout
            </MenuItem>
        </Menu>
    );

    const notifcation = (
        <Menu
            anchorEl={anchorNotificationEl}
            id="account-menu"
            open={notificationOpen}
            onClose={handleNotificationClose}
            onClick={handleNotificationClose}
            transformOrigin={{ horizontal: "right", vertical: "top" }}
            anchorOrigin={{ horizontal: "right", vertical: "bottom" }}
        >
        <TableContainer component={Paper}>
           <Table sx={{ minWidth: 850, border : 1, borderStyle : "solid" }} aria-label="simple table">
           <TableRow>
                <TableCell style={{fontWeight: "bold"}}>Assignment Name</TableCell>
                <TableCell style={{fontWeight: "bold"}} align="right">Course Name</TableCell>
                <TableCell style={{fontWeight: "bold"}} align="right">Due Date</TableCell>
                <TableCell style={{fontWeight: "bold"}} align="right">Confidence Probability</TableCell>
                <TableCell style={{fontWeight: "bold"}} align="right">Url</TableCell>
            </TableRow>
            {
                results.filter((e) => e.isSeen).map((entry, index) =>
                <TableRow>
                    <TableCell >{entry.assignment.title}</TableCell>
                    <TableCell align="right">{entry.assignment.courseName}</TableCell>
                    <TableCell align="right">{new Date(entry.assignment.dueDate).toDateString()}</TableCell>
                    <TableCell align="right">{entry.confidenceProbability * 100}</TableCell>
                    <TableCell align="right">
                        <a href={`//${entry.url}`}>
                            <Typography>Site Link</Typography>
                        </a>
                    </TableCell>
                </TableRow>
            )
            }
           </Table>
        </TableContainer> 
        </Menu>
    );

    return (
        <Box sx={{ flexGrow: 1 }}>
            <AppBar position="static" sx={{ background: "#404040" }}>
                <Toolbar>
                    <Link
                        href="/dashboard"
                        style={{
                            color: "white",
                            textDecoration: "none",
                            fontSize: "1.5rem",
                            fontFamily: "sans-serif",
                        }}
                    >
                        WolfWatch
                    </Link>
                    <Box sx={{ flexGrow: 1 }} />
                    <Box sx={{ display: { xs: "none", md: "flex" } }}>
                        <IconButton size="large" color="inherit" onClick={handleNotificationClick}>
                            <Badge badgeContent={badge} color="error">
                                <Notifications />
                            </Badge>
                        </IconButton>
                        <IconButton
                            size="large"
                            edge="end"
                            onClick={handleClick}
                            color="inherit"
                        >
                            <AccountCircle />
                        </IconButton>
                    </Box>
                </Toolbar>
            </AppBar>
            {menu}
            {notifcation}
        </Box>
    );
}
