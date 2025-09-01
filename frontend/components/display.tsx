"use client";

import axios from "axios";
import { useEffect, useState } from "react";
import { AlertCircle, Calendar, FileText, Loader2, Mail, RefreshCw, Upload, User } from "lucide-react";

import { ResumeDetails } from "./resume-details";

import { formatDate } from "@/lib/utils";
import { Resume, ResumeInfo } from "@/types/resume";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";


export const Display = () => {
    const [isLoading, setIsLoading] = useState(false);
    const [file, setFile] = useState<File | null>(null);
    const [isUploading, setIsUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [isDialogOpen, setIsDialogOpen] = useState(false);

    const [resumes, setResumes] = useState<Resume[]>([]);
    const [fetchingResume, setFetchingResume] = useState(false);
    const [resumeData, setResumeData] = useState<ResumeInfo | null>(null);
    const [selectedResume, setSelectedResume] = useState<ResumeInfo | null>(null);


    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            const selectedFile = e.target.files[0];
            const fileType = selectedFile.type;

            if(!fileType.includes("pdf") && !fileType.includes("word") && !fileType.includes("document")) {
                setError("Invalid file format. Please upload a PDF or DOCX file.");
                return;
            }

            if(selectedFile.size > 10 * 1024 * 1024) {  // 10MB limit
                setError("File is too large. Maximum size is 10MB.");
                return;
            } 

            setError(null);
            setFile(selectedFile);
        }
    }

    const fetchResumes = async () => {
        setFetchingResume(true);
        setError(null);

        try {
            const res = await axios.get("http://127.0.0.1:8000/api/v1/resumes/");
            setResumes(res.data);
            console.log("Fetched: ", res.data);
        } catch (error) {
            setError("Failed to fetch resumes. Please try again.");
            console.log("Fetch Error: ", error);
        } finally {
            setFetchingResume(false);
        }

    }

    useEffect(() => {
        fetchResumes();
    }, []);

    const handleUpload = async () => {
        if(!file) {
            setError("No file selected");
            return;
        }

        setIsUploading(true);
        setError(null);

        const formData = new FormData();
        formData.append("file", file);

        try {
            const res = await axios.post("http://127.0.0.1:8000/api/v1/resumes/upload", 
                formData,
                { 
                    headers: { "Content-Type": "multipart/form-data" },
                    timeout: 30000,   // 30 seconds timeout for large files 
                }
            );

            setResumeData(res.data)
            console.log("Res: ", res.data);
        } catch (error) {
            console.log("Error: ", error);
            setError("Failed to upload resume. Please try again.");
        } finally {
            setIsUploading(false);
        }
    }

    const handleViewDetails = async (id: number) => {
        setIsLoading(true);
        setError(null);

        try {
            const res = await axios.get(`http://127.0.0.1:8000/api/v1/resumes/${id}`);
            setSelectedResume(res.data);
            setIsDialogOpen(true);
        } catch (error) {
            console.log("Error: ", error);
            setError("Failed to fetch resume details. Please try again.");
        } finally {
            setIsLoading(false);
        }
    }


    return (
        <div className="container max-w-7xl p-4 mx-auto">
            <div className="mb-8">
                <h1 className="text-3xl font-bold mb-2">Resume Analyzer</h1>
                <p className="text-muted-foreground">
                    Upload resumes and get AI-powered analysis and insights
                </p>
            </div>

            <Tabs defaultValue="upload" className="">
                <TabsList className="max-w-md w-full mb-6 grid-cols-2">
                    <TabsTrigger value="upload" className="flex items-center gap-2">
                        <Upload className="h-4 w-4" />
                        Upload Resume
                    </TabsTrigger>
                    <TabsTrigger value="history" className="flex items-center gap-2">
                        <FileText className="h-4 w-4" />
                        Resume History
                    </TabsTrigger>
                </TabsList>

                {error && (
                    <Alert variant="destructive" className="mb-4">
                        <AlertCircle className="h-4 w-4" />
                        <AlertTitle>Error</AlertTitle>
                        <AlertDescription>{error}</AlertDescription>
                    </Alert>
                )}

                <TabsContent value="upload" className="space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>Upload your Resume</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="flex flex-col">
                                <Label className="mb-2">
                                    Select Resume File (PDF, DOCX)
                                </Label>
                                <div className="flex items-center gap-4">
                                    <Input 
                                        type="file"
                                        onChange={handleFileChange}
                                        accept=".pdf, .docx, .doc"
                                        className="cursor-pointer"
                                    />
                                    <Button 
                                        onClick={handleUpload}
                                        className="flex items-center cursor-pointer"
                                        disabled={isUploading || !file}
                                    >
                                        {isUploading ? (
                                            <>
                                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                                Uploading...
                                            </>
                                        ) : (
                                            <>
                                                <Upload className="mr-2 h-4 w-4" />
                                                Upload Resume
                                            </>
                                        )}
                                    </Button>
                                </div>
                                <p className="text-xs text-muted-foreground mt-1">
                                    Maximum file size: 10MB
                                </p>

                                {file && (
                                    <div className="flex items-center justify-between mt-4 p-3 bg-muted rounded-md">
                                            <FileText className="h-5 w-5 mr-2 text-primary" />
                                            <span className="text-sm font-medium">{file.name}</span>

                                        <p className="ml-auto text-xs font-bold">{(file.size / 1024).toFixed(2)} KB</p>
                                    </div>
                                )}
                            </div>
                        </CardContent>
                    </Card>

                    {resumeData && <ResumeDetails resume={resumeData} />}
                </TabsContent>

                <TabsContent value="history">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center justify-between">
                                <span>Resume History</span>

                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={fetchResumes}
                                    disabled={fetchingResume}
                                >
                                    {fetchingResume ? (
                                        <Loader2 className="h-4 w-4 animate-spin" />
                                    ) : (
                                        <>
                                            <RefreshCw className="h-4 w-4 mr-2" /> Refresh
                                        </>
                                    )}
                                </Button>
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            {fetchingResume ? (
                                <div className="flex items-center justify-center">
                                    <Loader2 className="h-8 w-8 animate-spin text-primary" />
                                </div>
                            ) : resumes.length == 0 ? (
                                <div className="py-8 text-center text-muted-foreground">
                                    <FileText className="h-12 w-12 mx-auto mb-3 opacity-20" />
                                    <p>No resumes have been uploaded yet</p>
                                    <Button
                                        size="sm"    
                                        variant="outline"
                                        className="mt-4"
                                        onClick={() => {
                                            const tabTrigger = document.querySelector<HTMLButtonElement>('button[data-value="upload"]');
                                            tabTrigger?.click();
                                        }}
                                    >
                                        Upload your first Resume
                                    </Button>
                                </div>
                            ) : (
                                <ScrollArea className="h-[500px]">
                                    <Table>
                                        <TableHeader>
                                            <TableRow>
                                                <TableHead>ID</TableHead>
                                                <TableHead>Filename</TableHead>
                                                <TableHead>Name</TableHead>
                                                <TableHead>Email</TableHead>
                                                <TableHead>Uploaded At</TableHead>
                                                <TableHead className="text-right">Actions</TableHead>
                                            </TableRow>
                                        </TableHeader>
                                        <TableBody>
                                            {resumes.map((resume) => (
                                                <TableRow key={resume.id} className="hover:bg-muted/50">
                                                    <TableCell className="font-medium">
                                                        {resume.id}
                                                    </TableCell>
                                                    <TableCell className="flex items-center gap-2">
                                                        <FileText className="h-4 w-4 text-primary" />
                                                        {resume.file_name}
                                                    </TableCell>
                                                    <TableCell>
                                                        <div className="flex items-center gap-2">
                                                            <User className="h-4 w-4 text-muted-foreground" />
                                                            {resume.name || "N/A"}
                                                        </div>
                                                    </TableCell>
                                                    <TableCell>
                                                        <div className="flex items-center gap-2">
                                                            <Mail className="h-4 w-4 text-muted-foreground" />
                                                            {resume.email || "N/A"}
                                                        </div>
                                                    </TableCell>
                                                    <TableCell>
                                                        <div className="flex items-center gap-2">
                                                            <Calendar className="h-4 w-4 text-muted-foreground" />
                                                            {formatDate(resume.uploaded_at)}
                                                        </div>
                                                    </TableCell>
                                                    <TableCell className="text-right">
                                                        <Button
                                                            variant="outline"
                                                            size="sm"
                                                            onClick={() => handleViewDetails(resume.id)}
                                                            disabled={
                                                                isLoading && selectedResume?.id === resume.id
                                                            }
                                                        >
                                                            {isLoading && selectedResume?.id === resume.id ? (
                                                                <Loader2 className="h-4 w-4 animate-spin" />
                                                                ) : (
                                                                "View Details"
                                                            )}
                                                        </Button>
                                                    </TableCell>
                                                </TableRow>
                                            ))}
                                        </TableBody>
                                    </Table>

                                    <ScrollBar orientation="horizontal" />
                                </ScrollArea>
                            )}
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>

            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                <DialogContent className="max-w-4xl max-h-[90vh] overflow-hidden">
                    <DialogHeader>
                        <DialogTitle>Resume Details</DialogTitle>
                    </DialogHeader>
                    {selectedResume && <ResumeDetails resume={selectedResume} />}
                </DialogContent>
            </Dialog>
        </div>
    );
};