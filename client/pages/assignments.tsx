import Layout from "@/components/DefaultLayout";
import { Box, Button, IconButton, Paper, Typography } from "@mui/material";
import React, { useEffect, useState } from "react";
import { Assignment } from "@/components/assignments/AssignmentTypes";
import { useAuth } from "@/components/AuthProvider";
import AssignmentModal from "@/components/assignments/AssignmentModal";
import AssignmentTable from "@/components/assignments/AssignmentTable"
import { Delete, Edit } from "@mui/icons-material";

export default function Assignments() {
    const { getCsrfToken } = useAuth();
    const [modalOpen, setModalOpen] = useState(false);
    const [assignments, setAssignments] = useState<Assignment[]>([]);
    const [targetedAssignment, setTargetedAssignment] = useState<Assignment | undefined>(undefined);
    const [selectedAssignments, setSelectedAssignments] = useState<Assignment[]>([]);
    const openAssignmentModal = (assignment: Assignment | undefined) => {
        setTargetedAssignment(assignment);
        setModalOpen(true);
    }

    const toggleAssignmentActive = async (assignment: Assignment) => {
        try {
            const response = await fetch(`/api/assignments/${assignment.assignmentId}`, {
                method: 'PUT',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-TOKEN': getCsrfToken() || ''
                },
                //send assignment as form data
                body: JSON.stringify({
                    dueDate: new Date(assignment.dueDate),
                    title: assignment.assignmentTitle,
                    courseName: assignment.className,
                    contents: assignment.assignmentText,
                    keyPhrases: assignment.keyPhrases,
                    assignmentActive: !assignment.assignmentActive //isActive not yet set so assignmentActive must be set to the opposite of isActive currently
                })
            });
            setAssignments(assignments.map((a) => {
                if (a.assignmentId === assignment.assignmentId) {
                    a.assignmentActive = !a.assignmentActive;
                }
                return a;
            }));
        } catch (error) {
            console.error("Error editing assignment: ", error);
        }
    }

    const fetchAssignments = async () => {
        try {
            const response = await fetch('/api/assignments', {
                method: 'GET',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-TOKEN': getCsrfToken() || ''
                }
            });
            if (response.ok) {
                const assignments = await response.json();
                console.log(assignments)
                setAssignments(assignments);
            } else {
                setAssignments([]);
            }
        } catch (error) {
            console.error("Error during logout:", error);
        }
    };

    // On mount, get assignments
    useEffect(() => {
        fetchAssignments();
    }, [getCsrfToken]);

    const submitAssignment = async (assignment: Assignment) => {
        if (assignment.assignmentId == undefined) {
            try {
                const response = await fetch('/api/assignments', {
                    method: 'POST',
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
                        assignmentActive: assignment.assignmentActive
                    })
                });
                if (response.ok) {
                    const newAssignment = await response.json();
                    setAssignments([...assignments, newAssignment]);
                } else {
                }
            } catch (error) {
                console.error("Error adding assignment: ", error);
            }
        } else {
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
                        assignmentActive: assignment.assignmentActive
                    })
                });
            } catch (error) {
                console.error("Error editing assignment: ", error);
            }
        }
        setModalOpen(false);
        fetchAssignments(); //re render assignments with changes made to the fields
    }

    const deleteAssignments = (assignmentsToDelete: Assignment[]) => {
        assignmentsToDelete.forEach(async assignment => {
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
            }
        });
        setAssignments(assignments => assignments.filter(assignment => !assignmentsToDelete.includes(assignment)));
    }

    const scanAssignment = async (assignment: Assignment) => {
        try {
            const response = await fetch(`/api/assignments/${assignment.assignmentId}/scan`, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-TOKEN': getCsrfToken() || ''
                }
            });
            alert("Scan Started!")
        } catch (error) {
            console.error("Error scanning assignment: ", error);
        }
    }

    return (
        <Layout>
            <Paper sx={{ padding: "0 10px 10px 10px", margin: "20px" }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
                    <Typography variant="h4" sx={{ textAlign: "center", margin: "20px", fontFamily: "bold" }}>Assignments</Typography>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <IconButton disabled={selectedAssignments.length != 1} onClick={() => openAssignmentModal(selectedAssignments[0])}>
                            <Edit />
                        </IconButton>
                        <IconButton disabled={selectedAssignments.length < 1} onClick={() => deleteAssignments(selectedAssignments)}>
                            <Delete />
                        </IconButton>
                        <Button disabled={selectedAssignments.length != 1} variant='contained' sx={{ margin: '10px' }}
                            onClick={() => scanAssignment(selectedAssignments[0])}>Scan!</Button>
                        <Button variant='contained' sx={{ margin: '10px' }} onClick={() => openAssignmentModal(undefined)}>
                            New Assignment
                        </Button>
                    </Box>
                </Box>
                <AssignmentTable assignments={assignments} setSelectedAssignments={setSelectedAssignments} toggleAssignmentActive={toggleAssignmentActive} />
            </Paper>
            <AssignmentModal
                open={modalOpen}
                close={() => setModalOpen(false)}
                submitAssignment={submitAssignment}
                initialValue={targetedAssignment}
            />
        </Layout >
    )
}
