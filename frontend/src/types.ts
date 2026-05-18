export interface User {
  id: number;
  username: string;
  email: string;
  role: string;
  role_display: string;
  tenant: number | null;
  tenant_name: string | null;
  branch: number | null;
  branch_name: string | null;
}

export interface LoginResponse extends User {
  token: string;
}

export interface Organization {
  id: number;
  name: string;
  slug: string;
  is_active: boolean;
}

export interface Vehicle {
  id: number;
  vin: string;
  make: string;
  model: string;
  year: number;
  license_plate: string;
  status: string;
  odometer_km: number;
}

export interface Transaction {
  id: number;
  transaction_type: string;
  amount: string;
  description: string;
  reference: string;
  occurred_at: string;
}

export interface AuditLog {
  id: number;
  action: string;
  model_name: string;
  object_repr: string;
  actor: number | null;
  created_at: string;
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
