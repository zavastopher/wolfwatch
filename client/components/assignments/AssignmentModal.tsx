import { useEffect, useRef, useState } from "react";
import { Assignment } from "./AssignmentTypes";
import { Box, Button, Chip, ClickAwayListener, Container, Dialog, DialogActions, DialogContent, DialogTitle, Fade, Grid, IconButton, Paper, Popper, PopperProps, TextField, Tooltip, Typography } from "@mui/material";
import { Close, Edit } from "@mui/icons-material";

export default function AssignmentModal({ open, close, submitAssignment, initialValue }: {
    open: boolean;
    close: () => void;
    submitAssignment: (assignment: Assignment) => void;
    initialValue: Assignment | undefined;
}) {

    const [assignmentTitle, setAssignmentTitle] = useState(initialValue?.assignmentTitle || '');
    const [className, setClassName] = useState(initialValue?.className || '');
    const [dueDate, setDueDate] = useState<string>('');
    const [assignmentText, setAssignmentText] = useState<string>(initialValue?.assignmentText || '');
    const [keyPhrases, setKeyPhrases] = useState<string[]>(initialValue?.keyPhrases || []);
    const [isTextInputPhase, setIsTextInputPhase] = useState<boolean>(true);

    const setDueDateFormatted = (dueDate: Date | string | undefined) => {
        const val = dueDate ? new Date(dueDate)?.toISOString()?.substring(0, 10) : ''
        setDueDate(val);
    }

    //update the assignment when it changes. Does not work if the assignment changes to undefined
    useEffect(() => {
        setAssignmentTitle(initialValue?.assignmentTitle || '');
        setClassName(initialValue?.className || '');
        setDueDateFormatted(initialValue?.dueDate);
        setAssignmentText(initialValue?.assignmentText || '');
        setKeyPhrases(initialValue?.keyPhrases || []);
        setIsTextInputPhase(true);
    }, [initialValue]);

    const handleClose = () => {
        close();
    }

    const handleSubmit = () => {
        submitAssignment({
            assignmentId: initialValue?.assignmentId,
            className: className,
            dueDate: new Date(dueDate),
            assignmentTitle: assignmentTitle,
            assignmentText: assignmentText,
            keyPhrases: keyPhrases,
            assignmentActive: true
        })
    };

    const handleChipDelete = (index: number) => () => {
        setKeyPhrases(keyPhrases.filter((_, i) => i !== index));
    }

    const addKeyPhrase = () => {
        const selection = window.getSelection();
        if (selection && selection.toString().trim() !== '') {
            keyPhrases.push(selection.toString());
            setKeyPhrases([...keyPhrases]);
            setPopupOpen(false);
            selection.empty();
        }
    }

    //popup handling
    const [popupOpen, setPopupOpen] = useState(false);
    const [anchorEl, setAnchorEl] = useState<PopperProps['anchorEl']>(null);

    const previousAnchorElPosition = useRef<DOMRect | undefined>(undefined);

    useEffect(() => {
        if (anchorEl) {
            if (typeof anchorEl === 'object') {
                previousAnchorElPosition.current = anchorEl.getBoundingClientRect();
            } else {
                previousAnchorElPosition.current = anchorEl().getBoundingClientRect();
            }
        }
    }, [anchorEl]);

    const handleMouseUp = () => {
        const selection = window.getSelection();

        // Resets when the selection has a length of 0
        if (!selection || selection.anchorOffset === selection.focusOffset || selection?.toString() === '') {
            setPopupOpen(false);
            return;
        }

        const getBoundingClientRect = () => {
            if (selection.rangeCount === 0 && previousAnchorElPosition.current) {
                setPopupOpen(false);
                return previousAnchorElPosition.current;
            }
            return selection.getRangeAt(0).getBoundingClientRect();
        }

        setPopupOpen(true);

        setAnchorEl({ getBoundingClientRect });
    };


    const id = open ? 'virtual-element-popper' : undefined;

    return (
        <Dialog
            onClose={handleClose}
            aria-labelledby="customized-dialog-title"
            open={open}>
            <DialogTitle sx={{ m: 0, p: 2 }} id="customized-dialog-title">
                {initialValue === undefined ? "Add Assignment" : "Edit Assignment"}
            </DialogTitle>
            <IconButton
                aria-label="close"
                onClick={handleClose}
                sx={{
                    position: 'absolute',
                    right: 8,
                    top: 8
                }}>
                <Close />
            </IconButton>
            <DialogContent dividers>
                <Grid container spacing={2}>
                    <Grid item xs={4}>
                        <TextField label="Assignment Title" variant="outlined" value={assignmentTitle} onChange={(e) => setAssignmentTitle(e.target.value)} />
                    </Grid>
                    <Grid item xs={4}>
                        <TextField label="Class" variant="outlined" value={className} onChange={(e) => setClassName(e.target.value)} />
                    </Grid>
                    <Grid item xs={4}>
                        <TextField label="Date" variant="outlined" type="date" value={dueDate} onChange={(e) => setDueDateFormatted(e.target.value)} InputLabelProps={{ shrink: true }} />
                    </Grid>
                    <Grid item xs={12}>
                        {isTextInputPhase ? (
                            <TextField
                                onChange={(e) => setAssignmentText(e.target.value)}
                                value={assignmentText}
                                multiline
                                label="Assignment Text"
                                variant="outlined"
                                sx={{ width: "510px" }} />
                        ) : (
                            <Container sx={{ display: "flex", alignItems: "flex-end" }} style={{ padding: 0 }}>
                                <Box border={1} borderRadius={1} padding={1} borderColor="divider">
                                    <Typography style={{ whiteSpace: "pre-wrap" }} onMouseUp={handleMouseUp} variant="body1">
                                        {assignmentText}
                                    </Typography>
                                </Box>
                                <IconButton onClick={() => setIsTextInputPhase(true)}>
                                    <Edit />
                                </IconButton>
                            </Container>
                        )}
                        <Popper
                            id={id}
                            open={popupOpen}
                            anchorEl={anchorEl}
                            transition
                            placement="bottom-start"
                            disablePortal>
                            {({ TransitionProps }) => (
                                <Fade {...TransitionProps} timeout={350}>
                                    <Paper>
                                        <ClickAwayListener onClickAway={() => setPopupOpen(false)}>
                                            <Button onClick={addKeyPhrase}>Add</Button>
                                        </ClickAwayListener>
                                    </Paper>
                                </Fade>
                            )}
                        </Popper>
                    </Grid>
                </Grid>
                <Grid item xs={6}>
                    <Box display="flex" alignItems={"center"} marginTop={1} columnGap={1}>
                        <Tooltip title="Click on the '+' button, then highlight a phrase to add to keyphrases">
                            <Typography>Key Phrases</Typography>
                        </Tooltip>
                        <Box display="flex" flexWrap="wrap" gap={0.5}>
                            {
                                keyPhrases?.map((phrase, index) => (
                                    <Chip key={index} label={phrase} variant="outlined" onDelete={handleChipDelete(index)} />
                                ))
                            }
                        </Box>
                        <Button sx={{ display: isTextInputPhase ? "block" : "none" }} onClick={() => setIsTextInputPhase(false)}>+</Button>
                    </Box>
                    <Typography sx={{ display: isTextInputPhase ? "none" : "block" }} variant="body2" color="textSecondary" fontStyle="italic">select text to add a key phrase</Typography>
                </Grid>
            </DialogContent>
            <DialogActions>
                <Button onClick={handleSubmit}>
                    Save
                </Button>
            </DialogActions>
        </Dialog >
    )
}
