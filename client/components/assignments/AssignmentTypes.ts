export type Assignment = {
    assignmentId: number | undefined,
    assignmentTitle: string,
    className: string,
    dueDate: Date,
    assignmentText: string,
    keyPhrases: string[],
    assignmentActive: boolean,
    lastScan: Date | undefined
}