import { useState } from "react";
import { Assignment } from "./AssignmentTypes";
import { useAuth } from "@/components/AuthProvider";
import { Box, Divider, IconButton, Paper, Switch, Typography } from "@mui/material";
import { Delete, Edit } from "@mui/icons-material";

export default function AssignmentCard({ assignment, openAssignmentModal, fetchAssignments }:
    {
        assignment: Assignment,
        openAssignmentModal: (assignment: Assignment) => void,
        fetchAssignments: () => void
    }) {
    const { getCsrfToken } = useAuth();
    const [isHovered, setIsHovered] = useState(false);
    const [isActive, setIsActive] = useState(true);
    const toggleAssignmentActive = async () => {
        try {
            const response = await fetch(`/api/assignments/${assignment.assignmentId}`, {
                method: 'PUT',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-TOKEN': getCsrfToken() || ''
                },
                // send assignment as form data
                body: JSON.stringify({
                    dueDate: assignment.dueDate,
                    title: assignment.assignmentTitle,
                    courseName: assignment.className,
                    contents: assignment.assignmentText,
                    keyPhrases: assignment.keyPhrases,
                    assignmentActive: !isActive //isActive not yet set so assignmentActive must be set to the opposite of isActive currently
                })
            });
            setIsActive(!isActive); //set isActive after assignment is successfully toggled
        } catch (error) {
            console.error("Error editing assignment: ", error);
        }
    }

    const deleteAssignment = async (assignment: Assignment) => {
        try {
            const response = await fetch(`/api/assignments/${assignment.assignmentId}`, {
                method: 'DELETE',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-TOKEN': getCsrfToken() || ''
                }
            });
        } catch (error) {
            console.error("Error editing assignment: ", error);
        }
        fetchAssignments();
    }

    return (
        <Paper
            sx={{ padding: "30px 20px", display: "flex", alignItems: "center", gap: "20px", position: "relative" }}
            elevation={isHovered ? 4 : 2}
            onMouseOver={() => setIsHovered(true)}
            onMouseOut={() => setIsHovered(false)}>
            <Typography variant="subtitle1">
                {`Due ${assignment.dueDate ? new Date(assignment.dueDate?.toString()).toLocaleDateString('en-US') : ''}`}
            </Typography>
            <Divider orientation="vertical" flexItem />
            <div>
                <Typography variant="h6">
                    {assignment.assignmentTitle}
                </Typography>
                <Typography variant="subtitle2">
                    {assignment.className}
                </Typography>
            </div>
            <Switch checked={isActive} onChange={toggleAssignmentActive} />
            {isHovered && <Box sx={{ position: "absolute", right: "10px" }}>
                <IconButton onClick={() => openAssignmentModal(assignment)}>
                    <Edit />
                </IconButton>
                <IconButton onClick={() => deleteAssignment(assignment)}>
                    <Delete />
                </IconButton>
            </Box>}
        </Paper>
    )
}